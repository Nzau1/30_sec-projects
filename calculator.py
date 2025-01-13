import streamlit as st

# Custom CSS for the app
def set_custom_css():
    st.markdown(
        """
        <style>
        /* App container styles */
        .app-container {
            background-color: #f9f9f9;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 30px auto;
            border-bottom: 5px solid #007acc;  /* Border only at the bottom */
        }

        /* Calculator operation buttons */
        .operation-buttons button {
            display: block;
            margin: 10px auto;
            background-color: #007acc;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 15px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }

        .operation-buttons button:hover {
            background-color: #00509e;
        }

        /* Align input fields */
        .stTextInput {
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Calculator function
def calculator():
    set_custom_css()  # Apply CSS styles

    # Main container with custom class
    st.markdown('<div class="app-container">', unsafe_allow_html=True)
    st.title("Enhanced Calculator")
    st.write("Perform basic arithmetic operations with style!")

    # Input fields
    num1 = st.number_input("Enter the first number", format="%.2f")
    num2 = st.number_input("Enter the second number", format="%.2f")

    # Operation buttons
    st.markdown('<div class="operation-buttons">', unsafe_allow_html=True)
    if st.button("Addition"):
        result = num1 + num2
        st.success(f"Result: {result}")
    if st.button("Subtraction"):
        result = num1 - num2
        st.success(f"Result: {result}")
    if st.button("Multiplication"):
        result = num1 * num2
        st.success(f"Result: {result}")
    if st.button("Division"):
        if num2 != 0:
            result = num1 / num2
            st.success(f"Result: {result}")
        else:
            st.error("Error: Division by zero is not allowed.")
    st.markdown('</div>', unsafe_allow_html=True)

    # End of container
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    calculator()
