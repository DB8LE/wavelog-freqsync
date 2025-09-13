from config import Config
from rigctld import RigctldConn
import time, traceback

def main():
    # Read config
    print("Reading config")
    config = Config().read_config()

    # Connect to rigctl
    print("Connecting to rigctld")
    rigctld_conn = RigctldConn(config.rigctld_host, config.rigctld_port)

    print("Starting")
    try:
        while True:
            if config.print_rig_data:
                print(rigctld_conn.get_frequency(), rigctld_conn.get_mode())
            time.sleep(config.update_delay)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, shutting down.")
    except Exception as e:
        print(f"Caught exception {e}, shutting down.")
        print(traceback.format_exc())
    finally:
        rigctld_conn.socket.close()

if __name__ == "__main__":
    main()
