import time
import global_vars, thread_control

def main():
    while True:
        if global_vars.close_session:
            thread_control.main()
        time.sleep(10.0)
    
main()