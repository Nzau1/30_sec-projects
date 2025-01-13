import streamlit as st
import random
import time

# Function to generate a random crash point
def generate_crash_point():
    return round(random.uniform(1.5, 25.0), 2)  # Random crash point between 1.5 and 5.0

# Function to simulate the Crash Game
def crash_game():
    st.title("Crash Game ✈️💥")
    st.write("Place your bet and cash out before the jet explodes!")

    # Initialize game state
    if "multiplier" not in st.session_state:
        st.session_state.multiplier = 1.0
        st.session_state.crash_point = generate_crash_point()
        st.session_state.running = False
        st.session_state.cash_out = False

    # Input for placing a bet
    bet = st.number_input("Place your bet ($)", min_value=1.0, step=0.5, value=10.0)

    # Button to start the game
    if st.button("Start"):
        st.session_state.multiplier = 1.0
        st.session_state.crash_point = generate_crash_point()
        st.session_state.running = True
        st.session_state.cash_out = False

        # Placeholder for jet and multiplier
        jet_placeholder = st.empty()
        multiplier_placeholder = st.empty()

        # Simulate the jet flying and multiplier increasing
        st.write("The jet is flying... 🚀")
        for i in range(100):
            if not st.session_state.running:
                break

            # Update multiplier
            st.session_state.multiplier = round(st.session_state.multiplier + 0.1, 2)
            
            # Update jet position
            jet_placeholder.markdown(f"<div style='font-size:30px; margin-left:{i*2}px;'>✈️</div>", unsafe_allow_html=True)
            multiplier_placeholder.write(f"Multiplier: **x{st.session_state.multiplier}**")
            time.sleep(0.2)

            # Check for crash
            if st.session_state.multiplier >= st.session_state.crash_point:
                st.session_state.running = False
                if not st.session_state.cash_out:
                    jet_placeholder.markdown("<div style='font-size:30px;'>💥</div>", unsafe_allow_html=True)
                    st.error(f"💥 Crash! The jet exploded at x{st.session_state.crash_point}. You lost your bet.")
                break

    # Cash Out Button
    if st.session_state.running and not st.session_state.cash_out:
        if st.button("Cash Out"):
            st.session_state.cash_out = True
            st.session_state.running = False
            winnings = round(bet * st.session_state.multiplier, 2)
            st.success(f"🎉 You cashed out at x{st.session_state.multiplier}! You won ${winnings}.")

    # Reset Button
    if not st.session_state.running:
        if st.button("Play Again"):
            st.session_state.multiplier = 1.0
            st.session_state.crash_point = generate_crash_point()
            st.session_state.running = False
            st.session_state.cash_out = False
            st.experimental_rerun()

# Run the Crash Game
if __name__ == "__main__":
    crash_game()
