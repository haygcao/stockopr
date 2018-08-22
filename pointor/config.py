
emulate = True

if emulate:
    wait_time_ll = 0.1
    wait_time_l = 0.1
    wait_time_m = 0.1
    wait_time_s = 0.1
    wait_time_ss = 0.1
    alert_interval_time = 1
    alert_startup_time = 1
else:
    wait_time_ll = 0.5 #10
    wait_time_l = 0.5 #5
    wait_time_m = 0.5 #1
    wait_time_s = 0.5
    wait_time_ss = 0.1
    alert_interval_time = 60
    alert_startup_time = 300

start_time_am = 0
start_time_pm = 0
