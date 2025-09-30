from config import Config
from rigctld import RigctldConn
from wavelog import WavelogConn
from typing import List
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

    print("\nStarting")
    last_freq = 0
    last_mode = "N/A"
    last_update = 0
    try:
        while True:
            time.sleep(config.update_delay)

            # Check if rig is off
            is_on = rigctld_conn.get_powerstate()
            if is_on == False:
                # If it is off, either wait until it is back on or exit based on config.
                if config.rigctld_allow_offline:
                    print("Rig is off")
                    rigctld_conn.wait_until_active()
                    time.sleep(5) # Wait a bit for rig to boot to avoid weirdness
                    print("Rig is back on")
                else:
                    print("ERROR: Rig is off")
                    exit(1)

            # Get data from rigctld
            freq = rigctld_conn.get_frequency()
            mode = rigctld_conn.get_mode()

            # Ignore mode responses starting with RPRT (does this happen with frequency too?)
            # TODO: is this a good idea? does more (like restarting the socket) need to be done?
            if mode.startswith("RPRT"):
                print("WARNING: Got mode response "+mode+". Ignoring.")
                continue

            # Send data to wavelog frequency or mode has changed
            last_update_seconds = time.time() - last_update
            if (last_freq != freq) or (last_mode != mode) or (last_update_seconds > config.wavelog_keepalive_sec):
                # Print rig data if enabled
                if config.print_rig_data:
                    print(freq, mode)

                # Send to wavelog for all connections
                for conn in wavelog_conns:
                    conn.set_rig_freq_mode(config.wavelog_radio_name, freq, mode)
                
                last_freq = freq
                last_mode = mode
                last_update = time.time()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, shutting down.")
    except Exception as e:
        print(f"Caught exception {e}, shutting down.")
        print(traceback.format_exc())
    finally:
        rigctld_conn.socket.close()

if __name__ == "__main__":
    main()
