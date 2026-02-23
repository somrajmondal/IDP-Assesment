# from transformers import AutoModelForCausalLM, AutoTokenizer


from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
device = "cuda" # the device to load the model onto

# model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
# tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
path = 'Qwen/Qwen2-VL-7B-Instruct'
model = Qwen2VLForConditionalGeneration.from_pretrained(
            path,
            torch_dtype='auto',
            device_map="auto",
        ).eval()
min_pixels = 256 * 28 * 28
max_pixels = 1280 * 28 * 28
processor = AutoProcessor.from_pretrained(
    path, min_pixels=min_pixels, max_pixels=max_pixels
)

model.save_pretrained("LLM_Model/")
processor.save_pretrained("LLM_Model/")

# from langchain.embeddings import HuggingFaceInstructEmbeddings

# embed_model = HuggingFaceInstructEmbeddings(
#     model_name="hkunlp/instructor-large", model_kwargs={"device": device}
# )

# import pickle
# model_file = open('hkunlp_instructor_large.bin', 'ab')
     
#     # source, destination
# pickle.dump(embed_model, model_file) 
# model_file.close()


# from gliner import GLiNER

# model = GLiNER.from_pretrained("numind/NuNerZero")

# model.save_pretrained("NER_Model/")
