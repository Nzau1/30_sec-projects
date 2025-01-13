import streamlit as st

# To-Do List function
def todo_list():
    st.title("To-Do List")
    st.write("Manage your daily tasks here.")

    # Create a list to store tasks (for demo, we will use session_state to persist tasks)
    if "tasks" not in st.session_state:
        st.session_state.tasks = []

    # Add new task input
    new_task = st.text_input("Add a new task")

    if st.button("Add Task"):
        if new_task:
            st.session_state.tasks.append(new_task)
            st.success(f"Task '{new_task}' added!")
        else:
            st.warning("Please enter a task.")

    # Display tasks
    if st.session_state.tasks:
        st.write("### Your Tasks:")
        for index, task in enumerate(st.session_state.tasks):
            task_container = st.container()
            task_container.write(f"- {task}")
            if st.button(f"Delete {task}", key=task):
                st.session_state.tasks.remove(task)
                task_container.empty()
                st.success(f"Task '{task}' deleted!")
    else:
        st.write("No tasks added yet. Start by adding a task!")

if __name__ == "__main__":
    todo_list()
