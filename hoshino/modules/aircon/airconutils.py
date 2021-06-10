import datetime
import os
import hoshino

try:
    import ujson as json
except:
    import json

R = 8.314  # 理想气体常数
i = 6  # 多分子气体自由度
K = 273  # 开氏度
vgas = 22.4  # 气体摩尔体积
unit_volume = 2  # 每人体积
aircon_off = 0.05  # 关空调后每秒温度变化量
ac_volume = [0.178, 0.213, 0.267]  # 每秒进风量
powers = [5000, 6000, 7500]  # 功率
volume_text = ["低", "中", "高"]

ac_central_power = 7500
ac_central_windrate = 0.577
ac_central_unit_volume = 100

AIRCON_HOME = 0
AIRCON_CENTRAL = 1

required_ranges = {
    "set_temp": (-273, 999999, 26),
    "env_temp": (-273, 999999, 33),
    "wind_rate": (0, 2, 0),
    "balance": (-1000000, 1000000, 0),
    "ac_type": (0, 1, 0)
}


def sgn(diff):
    return 1 if diff > 0 else -1 if diff < 0 else 0


def get_group_aircon(builtin_path):
    global required_ranges

    filename = os.path.join(os.path.dirname(builtin_path), 'aircon.json')

    try:
        with open(filename, encoding='utf8') as f:
            aircons = json.load(f)

            for gid in aircons:
                aircon = aircons[gid]
                for item in required_ranges:
                    low, high, default = required_ranges[item]
                    if (item not in aircon) or (not low <= aircon[item] <= high):
                        aircon[item] = default

            return aircons

    except Exception as e:
        return {}


def write_group_aircon(builtin_path, aircons):
    filename = os.path.join(os.path.dirname(builtin_path), 'aircon.json')
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(aircons, f, ensure_ascii=False)


def new_aircon(num_member, set_temp=26, now_temp=33):
    volume = max(num_member * unit_volume, 20)
    return {"is_on": True, "env_temp": now_temp, "now_temp": now_temp,
            "set_temp": set_temp, "last_update": now_second(),
            "volume": volume, "wind_rate": 0, "balance": 0, "ac_type": AIRCON_HOME}


def now_second():
    return int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())


def get_temp(N, n, setting, prev, T, power):
    direction = sgn(setting - prev)
    threshold = power / (n * 1000 / vgas) / (i / 2) / R
    cps = power / (N * 1000 / vgas) / (i / 2) / R

    if (abs(setting - prev) - threshold) >= cps * T:
        new_temp = prev + direction * cps * T
    else:
        t1 = max(0, int((abs(setting - prev) - threshold) / cps))
        temp1 = prev + direction * cps * t1
        new_temp = (1 - n / N) ** (T - t1 - 1) * (temp1 - setting) + setting
    return round(new_temp, 1)


def update_aircon(aircon):
    if aircon["is_on"]:
        now_temp = aircon["now_temp"]
        last_update = aircon["last_update"]
        volume = aircon["volume"]
        set_temp = aircon["set_temp"]
        power = powers[aircon["wind_rate"]]
        wind_rate = ac_volume[aircon["wind_rate"]]

        new_update = now_second()
        t_delta = new_update - last_update

        ac_type = aircon["ac_type"]
        if ac_type == AIRCON_HOME:
            power = powers[aircon["wind_rate"]]
            wind_rate = ac_volume[aircon["wind_rate"]]
        elif ac_type == AIRCON_CENTRAL:
            power = (volume // ac_central_unit_volume + 1) * ac_central_power
            wind_rate = (volume // ac_central_unit_volume + 1) * ac_central_windrate
        else:  # should never reach here
            pass

        new_temp = get_temp(volume, wind_rate, set_temp, now_temp, t_delta, power)

        aircon["now_temp"] = new_temp
        aircon["last_update"] = new_update

    else:
        env_temp = aircon["env_temp"]
        now_temp = aircon["now_temp"]
        last_update = aircon["last_update"]
        new_update = now_second()
        timedelta = new_update - last_update

        direction = sgn(env_temp - now_temp)
        new_temp = now_temp + direction * timedelta * aircon_off
        if (env_temp - now_temp) * (env_temp - new_temp) < 0:  # 过头了
            new_temp = env_temp

        aircon["now_temp"] = new_temp
        aircon["last_update"] = new_update


def print_aircon(aircon):
    wind_rate = aircon["wind_rate"]
    now_temp = aircon["now_temp"]
    set_temp = aircon["set_temp"]
    env_temp = aircon["env_temp"]

    text = f"当前风速{volume_text[wind_rate]}\n" if (aircon["is_on"] and aircon["ac_type"] == AIRCON_HOME) else ""

    text += f'''
当前设置温度 {set_temp} °C
当前群里温度 {round(now_temp, 1)} °C
当前环境温度 {env_temp} °C'''.strip()

    return text
