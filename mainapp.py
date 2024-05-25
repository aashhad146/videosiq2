import streamlit as st
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image
from youtubesearchpython import VideosSearch
from duckduckgo_search import ddg_images
from concurrent.futures import ThreadPoolExecutor


# CSS for backgorund image
custom_css = """
    <style>
   
    .main.css-k1vhr4.egzxvld3{
    background: radial-gradient(circle, rgba(238,174,202,1) 0%, rgba(148,187,233,1) 100%) !important;
    }
   
        # .main.css-k1vhr4.egzxvld3 {
        #     background-image: url("https://i.ibb.co/xjWqPvq/Picture1.png");
        #     background-size: cover;
        #     background-position: center;
        #     background-repeat: no-repeat;
        }
    </style>
"""
# Apply the custom CSS to the Streamlit app background
st.markdown(custom_css, unsafe_allow_html=True)
# Load the model, image processor, and tokenizer only once
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Set generation parameters
max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

# Initialize the search history list
search_history = []

# Streamlit app
def main():
    # Create a sidebar to display search history
    st.sidebar.header("Search History")

    # Create a selectbox to choose between image and video search
    search_option = st.sidebar.selectbox("Select Search Option", ["Image Search", "Video Search"])

    if search_option == "Image Search":
        image_search()
    else:
        video_search()

# Function to predict captions for an image
@st.cache
def predict_caption(image_path):
    try:
        i_image = Image.open(image_path)
        if i_image.mode != "RGB":
            i_image = i_image.convert(mode="RGB")
        i_image = i_image.resize((256, 256))  # Resize for faster processing
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return ["Error: No valid images provided."]

    pixel_values = feature_extractor(images=[i_image], return_tensors="pt").pixel_values.to(device)
    output_ids = model.generate(pixel_values, **gen_kwargs)
    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    return preds

# Function to perform image search
# Streamlit app
def image_search():
    st.title("Image-Based Image Search Lens")

    # Upload an image
    image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if image is not None:
        # Display the uploaded image and its name
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.write("Uploaded Image Name:", image.name)

        # Generate a caption for the image
        def process_image():
            try:
                i_image = Image.open(image)
                if i_image.mode != "RGB":
                    i_image = i_image.convert(mode="RGB")
                i_image = i_image.resize((256, 256))  # Resize for faster processing

                pixel_values = feature_extractor(images=[i_image], return_tensors="pt").pixel_values.to(device)
                output_ids = model.generate(pixel_values, **gen_kwargs)
                preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
                preds = [pred.strip() for pred in preds]
                return preds
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                return []

        with st.spinner("Analyzing Image, Please Wait..."):
            with ThreadPoolExecutor() as executor:
                future = executor.submit(process_image)
                preds = future.result()

        if preds:
            # Display the GC your image contain
            st.subheader("Your Image are:")
            st.write(preds[0])

            # Add the generated caption to the search history
            search_history.append(preds)

            # Display the search history in the image sidebar
            st.sidebar.header("Image Search History")
            for caption in search_history:
                st.sidebar.text(caption)

            # Perform a Image search based on the GC your image
            search_query = preds[0]
            st.subheader("Related Image Search Results:")

            # Fetch and display a smaller number of images initially
            num_images_to_display = 10
            displayed_images = 0

            for img in ddg_images(search_query, max_results=30):
                # Use st.image to display the images
                st.image(img['image'], caption="Image")
                displayed_images += 1

                if displayed_images >= num_images_to_display:
                    break
        else:
            st.write("No captions generated for the uploaded image.")
# Function to perform YouTube search
@st.cache
def perform_youtube_search(yt_search_query):
    try:
        videos_search = VideosSearch(yt_search_query, limit=10)  # Limit to 10 results
        results = videos_search.result()
        return results['result'] if results and 'result' in results else []
    except Exception as e:
        st.error(f"Error performing YouTube search: {str(e)}")
        return []
# Function to perform YouTube search
def video_search():
    st.title("Image-Based Query Search on YouTube")

    # Create a sidebar to display search history
    st.sidebar.header("Search History")
    for caption in search_history:
        st.sidebar.text(caption)

    # Upload an image
    image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if image is not None:
        # Display the uploaded image and its name
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.write("Uploaded Image Name:", image.name)

        # Generate a caption for the image
        with st.spinner("Analyzing Image Please Wait a Second..."):
            
            captions = predict_caption(image)
            generated_caption = captions[0]

        # Display the generated caption
        st.subheader("After Analyze Image the Image has:")
        st.write(generated_caption)

        # Add the generated caption to the search history
        search_history.append(generated_caption)

        # Perform a YouTube search based on the generated caption
        yt_search_query = generated_caption
        st.subheader("YouTube Search Results:")
        st.write("Performing YouTube search for:", yt_search_query)

        # Use threading to perform the YouTube search in the background
        results = perform_youtube_search(yt_search_query)

        if results:
            st.write("Playlist of Videos Matching the Caption:")
            for video in results:
                video_title = video['title']
                video_id = video['id']

                # Embed the YouTube video player with the correct URL
                iframe_url = f"https://www.youtube.com/embed/{video_id}"
                st.components.v1.iframe(iframe_url, height=315)
                st.write(f"Video Title: {video_title}")

        else:
            st.write("No search results found on YouTube.")


if __name__ == "__main__":
    main()
