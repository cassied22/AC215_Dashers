"""Streamlit app for Recipe Recommendation System."""
import os
import sys

import streamlit as st

from dotenv import load_dotenv


# from langchain.embeddings import OpenAIEmbeddings
# from langchain_community.vectorstores import Chroma
# from streamlit_option_menu import option_menu


# Must be the first Streamlit command
st.set_page_config(page_title="Recipe Assistant", page_icon="🍳", layout="wide", initial_sidebar_state="expanded")

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, "src")
sys.path.append(src_path)

# Import project modules
from datapipeline.cli_rag import process_query
from food_detection.gemini_object_detection import detect_objects
from food_detection.gemini_object_detection import get_ingredient_details
from food_detection.gemini_object_detection import test_model_availability


load_dotenv()


def setup_vector_db():
    """Initialize ChromaDB connection."""
    try:
        embeddings = OpenAIEmbeddings()
        persist_directory = os.path.join(src_path, "datapipeline/outputs/chroma_db")
        vector_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        return vector_db
    except Exception as e:
        st.error(f"Failed to initialize vector database: {str(e)}")
        return None


def ingredient_detection_section(vector_db):
    """Render the ingredient detection section."""
    st.title("🔍 Ingredient Detection")

    # Add model test button in a small container
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔧 Test Gemini Connection", help="Check if the Gemini API is working"):
                with st.spinner("Testing connection..."):
                    result = test_model_availability()
                    if "successful" in result:
                        st.success(result)
                    else:
                        st.error(f"Connection failed: {result}")

    # Main detection interface
    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Upload an image of your ingredients",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear, well-lit image of your ingredients. Supported formats: JPG, JPEG, PNG",
        )

        if uploaded_file:
            try:
                st.image(uploaded_file, caption="Image Preview", use_container_width=True)

                if st.button("🔎 Analyze Ingredients", type="primary", help="Start ingredient detection"):
                    with st.spinner("Analyzing image..."):
                        try:
                            detected_ingredients = detect_objects(uploaded_file)

                            if detected_ingredients:
                                st.session_state["detected_ingredients"] = detected_ingredients
                                st.success("✨ Detection Complete!")

                                # Display ingredients in a nice format
                                st.markdown("### 🥗 Detected Ingredients")
                                for ingredient in detected_ingredients:
                                    st.markdown(f"- {ingredient}")

                                # Get additional details
                                with st.spinner("Getting ingredient information..."):
                                    details = get_ingredient_details(detected_ingredients)
                                    if details:
                                        st.session_state["ingredient_details"] = details
                            else:
                                st.warning("👀 No ingredients detected. Try uploading a clearer image.")

                        except Exception as e:
                            st.error("❌ Detection failed")
                            st.error(f"Error details: {str(e)}")
                            st.info("💡 Tip: Make sure your image is clear and well-lit")
            except Exception as e:
                st.error("Failed to process image")
                st.error(f"Error details: {str(e)}")

    # Results column
    with col2:
        if "detected_ingredients" in st.session_state:
            # Recipe recommendations
            if st.button("👨‍🍳 Find Matching Recipes", type="primary"):
                with st.spinner("Searching for perfect recipes..."):
                    query = (
                        f"Find recipes using these ingredients: {', '.join(st.session_state['detected_ingredients'])}"
                    )
                    recommendations = process_query(query, vector_db)

                    if recommendations:
                        st.success("🎉 Found these recipes for you!")
                        for i, recipe in enumerate(recommendations, 1):
                            with st.expander(f"🍳 Recipe {i}: {recipe.get('title', 'Untitled')}"):
                                st.markdown("**📝 Ingredients needed:**")
                                for ingredient in recipe.get("ingredients", []):
                                    st.markdown(f"- {ingredient}")

                                st.markdown("**👩‍🍳 Instructions:**")
                                for j, step in enumerate(recipe.get("directions", []), 1):
                                    st.markdown(f"{j}. {step}")

            # Ingredient details
            if "ingredient_details" in st.session_state:
                with st.expander("📌 Ingredient Information", expanded=True):
                    details = st.session_state["ingredient_details"]

                    if "shelf_life" in details:
                        st.markdown("**🕒 Shelf Life:**")
                        st.markdown(details["shelf_life"])

                    if "storage" in details:
                        st.markdown("**🗄️ Storage Tips:**")
                        st.markdown(details["storage"])

                    if "recipes" in details:
                        st.markdown("**🥘 Common Recipe Ideas:**")
                        if isinstance(details["recipes"], list):
                            for recipe in details["recipes"]:
                                st.markdown(f"- {recipe}")
                        else:
                            st.markdown(details["recipes"])


def recipe_search_section(vector_db):
    """Render the recipe search section."""
    # [Previous code remains the same]


def recommendation_section(vector_db):
    """Render the recommendation section."""
    # [Previous code remains the same]


def main():
    """Run the app."""
    # Initialize vector database
    vector_db = setup_vector_db()

    if vector_db is None:
        st.error("Failed to initialize vector database. Please check your configuration.")
        return

    with st.sidebar:
        selected = option_menu(
            "🍽️ Recipe Assistant",
            ["Home", "Ingredient Detection", "Recipe Search", "Recipe Recommendations"],
            icons=["house", "camera", "search", "book"],
            default_index=0,
            key="menu_selection",
        )

    if selected == "Home":
        st.title("🏠 Recipe Assistant")
        st.markdown(
            """
        ## Welcome to your personal recipe assistant!

        This app helps you:
        - 📸 Detect ingredients from images
        - 🔍 Search through our recipe database
        - 👨‍🍳 Get recipe recommendations based on your ingredients

        Choose an option from the sidebar to get started!
        """
        )

        # Add some featured recipes or tips
        st.markdown("### 💡 Quick Tips")
        st.markdown(
            """
        - Use clear, well-lit images for best ingredient detection
        - Try searching by cuisine type or dietary preferences
        - List all available ingredients for better recommendations
        """
        )

    elif selected == "Ingredient Detection":
        ingredient_detection_section(vector_db)

    elif selected == "Recipe Search":
        recipe_search_section(vector_db)

    elif selected == "Recipe Recommendations":
        recommendation_section(vector_db)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)
