from config import Config
from rigctld import RigctldConn
from wavelog import WavelogConn, WavelogCallbackListener
from typing import List
from collections import deque
import time, traceback

def main():
    # Read config
    print("Reading config")
    config = Config().read_config()

    # Connect to rigctl
    print("Connecting to rigctld")
    rigctld_conn = RigctldConn(config.rigctld_host, config.rigctld_port)

    # Initialize wavelog connections
    wavelog_conns: List[WavelogConn] = []
    for api_key in config.wavelog_api_keys:
        wavelog_conns.append(WavelogConn(config.wavelog_host, api_key))

    # Initialize wavelog callback listener
    wavelog_callback_queue = deque(maxlen=1)
    wavelog_callback_listener = WavelogCallbackListener(config.wavelog_callback_port, wavelog_callback_queue)

    print("\nStarting")
    last_freq = 0
    last_mode = "N/A"
    last_update = 0

    # If enabled start wavelog callback listener
    if config.wavelog_enable_callbacks:
        wavelog_callback_listener.start()

    try:
        # Enter main processing loop
        while True:
            # Check if rig is off
            is_on = rigctld_conn.get_powerstate()
            if not is_on:
                # If it is off, either wait until it is back on or exit based on config.
                if config.rigctld_allow_offline:
                    print("Rig is off")
                    rigctld_conn.wait_until_active()
                    time.sleep(config.rigctld_boot_time) # Wait a bit for rig to boot to avoid weirdness
                    print("Rig is back on")
                    wavelog_callback_queue.clear() # Don't process any old callbacks
                else:
                    print("ERROR: Rig is off")
                    exit(1)

            # Check for callbacks TODO: move this to seperate thread
            if len(wavelog_callback_queue) > 0:
                # Send frequency and mode to wavelog
                callback_freq, callback_mode = wavelog_callback_queue[0]
                for conn in wavelog_conns:
                    conn.set_rig_freq_mode(config.wavelog_radio_name, callback_freq, callback_mode)

                # Send requested frequency and mode to rigctld
                rigctld_conn.set_frequency(callback_freq)
                rigctld_conn.set_mode(callback_mode)

                # Clear callback queue for next run and resart loop
                wavelog_callback_queue.clear()
                
                time.sleep(0.1) # sleep a little for safety
                continue

            # Only wait the update delay if we made it to here
            time.sleep(config.update_delay)

            # Get data from rigctld
            callback_freq = rigctld_conn.get_frequency()
            callback_mode = rigctld_conn.get_mode()

            # Ignore mode responses starting with RPRT (does this happen with frequency too?)
            # TODO: is this a good idea? does more (like restarting the socket) need to be done?
            if callback_mode.startswith("RPRT"):
                print("WARNING: Got mode response "+callback_mode+". Ignoring.")
                continue

            # Send data to wavelog frequency or mode has changed
            last_update_seconds = time.time() - last_update
            if (last_freq != callback_freq) or (last_mode != callback_mode) or (last_update_seconds > config.wavelog_keepalive_sec):
                # Print rig data if enabled
                if config.print_rig_data:
                    print(callback_freq, callback_mode)

                # Send to wavelog for all connections
                for conn in wavelog_conns:
                    conn.set_rig_freq_mode(config.wavelog_radio_name, callback_freq, callback_mode)
                
                last_freq = callback_freq
                last_mode = callback_mode
                last_update = time.time()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, shutting down.")
    except Exception as e:
        print(f"Caught exception {e}, shutting down.")
        print(traceback.format_exc())
    finally:
        rigctld_conn.socket.close()
        wavelog_callback_listener.close()

if __name__ == "__main__":
    main()
