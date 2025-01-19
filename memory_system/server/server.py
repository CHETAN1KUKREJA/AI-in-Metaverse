from flask import Flask, request, jsonify
from queue import Queue
from ServerBuilderCode.memory_rater import QuantizedMemoryRater
from embedding_model.SFRMistralRetriever import SFRMistralRetriever
from embedding_model.baseRetriever import BaseRetriever, QuantizationConfig, QuantizationType
from ServerBuilderCode.queueManagerEmbedding import EmbeddingQueueManager
from embedding_model.minilmv6 import MiniLMv6Retriever 
from planner_model.model import QuantizedPlanner
from huggingface_hub import login
# Replace 'your_token_here' with your Hugging Face access token
token = "enter_your_token_here"

# Log in to Hugging Face Hub
login(token)

print("Successfully logged in to Hugging Face Hub!")


app = Flask(__name__)
rater = QuantizedMemoryRater()
planner= QuantizedPlanner()

# config = QuantizationConfig(quant_type=QuantizationType.INT4_NESTED)
# embedding_model = SFRMistralRetriever(quantization=config)

embedding_model = MiniLMv6Retriever()
embedding_queue_manager = EmbeddingQueueManager(embedding_model)
request_queue_rate = Queue()
request_queue_planner = Queue()

@app.route('/rate', methods=['POST'])
def rate():
    data = request.get_json()
    memory = data.get('memory')
    if not memory:
        return jsonify({'error': 'Missing memory'}), 400

    # Add request to the queue
    request_queue_rate.put(memory)

    # Process the queue
    while not request_queue_rate.empty():
        memory = request_queue_rate.get()
        try:
            result = rater.rate_memory(memory)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/plan', methods=['POST'])
def plan():
    data = request.get_json()
    memory = data.get('memory')
    if not memory:
        return jsonify({'error': 'Missing memory'}), 400

    # Add request to the queue
    request_queue_planner.put(memory)

    # Process the queue
    while not request_queue_planner.empty():
        memory = request_queue_planner.get()
        try:
            result = planner.plan_memory(memory)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/embed', methods=['POST'])
def embed():
    """Endpoint for text embedding"""
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'Missing text'}), 400
        
    # Queue the embedding request and get an ID
    request_id = embedding_queue_manager.add_request(text)
    
    # Wait for and return the result
    result = embedding_queue_manager.get_result(request_id)
    return jsonify(result)

if __name__ == '__main__':
    app.run()