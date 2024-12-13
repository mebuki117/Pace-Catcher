# v0.1.0

import os
import datetime
import time
import requests
import re

path_current = f'{os.path.dirname(os.path.realpath(__file__))}'
path_allnames = f'{path_current}/data/allnames.txt'
path_paces = f'{path_current}/data/allpaces.txt'
path_temp = f'{path_current}/data/temp.txt'
path_dir = f'{path_current}/data'

sent_world_ids = {}
sent_user = {}


# Main
def send_priority():
  global sent_world_ids, sent_user

  while True:
    try:
      data = fetch_data()

      current_world_ids = {entry['worldId'] for entry in data if 'worldId' in entry}
      removed_world_ids = set(sent_world_ids.keys()) - current_world_ids
      sent_world_ids = {world_id: sent_world_ids[world_id] for world_id in sent_world_ids if world_id in current_world_ids}

      # log time
      logtime = datetime.datetime.now()
      print(f'[{logtime}] waiting pace...')

      allname = getallnames(path_allnames, path_dir)
      for removed_world_id in removed_world_ids:
        if removed_world_id in sent_user:
          for l in range(len(allname)):
            if allname[l] == sent_user[removed_world_id]:
              with open(path_temp, 'w', encoding='utf-8') as f:
                f.write(f'{sent_user[removed_world_id]} : {allname[l+1]}')
                f.write(f'\n0')
              print(f'[{logtime}] send priority: {sent_user[removed_world_id]} : {allname[l+1]}/0')
              print(f'[{logtime}] del world_id from sent_user: {removed_world_id}')
              del sent_user[removed_world_id]
              break

      for entry in data:
        world_id = entry['worldId']
        is_cheated = entry.get('isCheated', False)

        if is_cheated and world_id in sent_user:
          for l in range(len(allname)):
            if allname[l] == sent_user[world_id]:
              with open(path_temp, 'w', encoding='utf-8') as f:
                f.write(f'{sent_user[world_id]} : {allname[l+1]}')
                f.write(f'\n0')
              print(f'[{logtime}] send priority: {sent_user[world_id]} : {allname[l+1]}/0')
              print(f'[{logtime}] del world_id from sent_user: {world_id}')
              del sent_user[world_id]
              break

      for entry in data:
        # get world data
        world_id = entry['worldId']
        event_list = entry.get('eventList', [])

        if event_list:
          max_event = max(
            event_list,
            key=lambda event: event.get('igt', -1),
            default=None
          )
          max_igt = max_event.get('igt', -1) if max_event else -1
          event_id = max_event.get('eventId', None)

          if world_id not in sent_world_ids or max_igt > sent_world_ids[world_id][1]:
            # get basic data
            game_version = entry.get('gameVersion', None)
            if game_version != '1.16.1':
              continue
            nickname = entry['nickname']
            uuid = entry.get('user', {}).get('uuid', None)
            live_account = entry.get('user', {}).get('liveAccount', None)
            item_data = entry.get('itemData', {}).get('estimatedCounts', {})
            ender_pearl_count = item_data.get('minecraft:ender_pearl', None)
            blaze_rod_count = item_data.get('minecraft:blaze_rod', None)

            # log time
            logtime = datetime.datetime.now()

            # get all pace
            list_pace = get_all_pace(path_paces)
            if list_pace == -1:
              # log
              print(f'[{logtime}] not exist pacemanbot-runner-pbpaces channel')

            found = False
            for i in range(0, len(list_pace), 7):
              if list_pace[i] in nickname:
                # add :00
                for m in range(1, 7):
                  if list_pace[i + m].find(':') == -1:
                    list_pace[i + m] = f'{list_pace[i + m]}:00'
                found = True
                break

            # continue if user not found
            if not found:
              time.sleep(2)
              continue

            # continue if not in events
            if event_id not in {'rsg.enter_bastion', 'rsg.enter_fortress', 'rsg.first_portal', 'rsg.enter_stronghold', 'rsg.enter_end', 'rsg.credits'}:
              time.sleep(2)
              continue

            # log
            print(f'[{logtime}] {list_pace}')
            print(
              f'[{logtime}] worldId: {world_id}\n'
              f'[{logtime}] eventId: {event_id}, igt: {max_igt}\n'
              f'[{logtime}] gameVersion: {game_version}\n'
              f'[{logtime}] nickname: {nickname}\n'
              f'[{logtime}] uuid: {uuid}\n'
              f'[{logtime}] liveAccount: {live_account}\n'
              f'[{logtime}] ender_pearl: {ender_pearl_count}, blaze_rod: {blaze_rod_count}'
            )
            print(f'[{logtime}] name, pb pace and pb: {list_pace[i]}/{list_pace[i+1]}/{list_pace[i+2]}/{list_pace[i+3]}/{list_pace[i+4]}/{list_pace[i+5]}/{list_pace[i+6]}') # name/fs/ss/b/e/ee/pb

            # set data
            now_igt = convert_to_hh_mm_ss(max_igt)
            ss_time = list_pace[i + 2]
            b_time = list_pace[i + 3]
            e_time = list_pace[i + 4]
            ee_time = list_pace[i + 5]
            pb_time = list_pace[i + 6]

            # priorities: -1=NoPlayer, 0=Nothing, 1=FS, 3=SS, 4=B, 5=E, 6=SSPB, 7=EE, 8=FIN, 9=BPB, 10=EPB, 11=EEPB, 12=NPB
            priority = 0

            if event_id == 'rsg.enter_bastion' or event_id == 'rsg.enter_fortress':
              if world_id in sent_world_ids:
                if (sent_world_ids[world_id][0] == 'rsg.enter_bastion' or sent_world_ids[world_id][0] == 'rsg.enter_fortress') and (ender_pearl_count or blaze_rod_count):
                  if time_to_seconds(ss_time) > time_to_seconds(now_igt):
                    priority = 6
                  else:
                    priority = 3
                else:
                  priority = 1
              else:
                priority = 1

            elif event_id == 'rsg.first_portal':
              if time_to_seconds(b_time) > time_to_seconds(now_igt):
                priority = 9
              else:
                priority = 4

            elif event_id == 'rsg.enter_stronghold':
              if time_to_seconds(e_time) > time_to_seconds(now_igt):
                priority = 10
              else:
                priority = 5

            elif event_id == 'rsg.enter_end':
              if time_to_seconds(ee_time) > time_to_seconds(now_igt):     
                priority = 11
              else:
                priority = 7

            elif event_id == 'rsg.credits':
              if time_to_seconds(pb_time) > time_to_seconds(now_igt):
                priority = 12
              elif time_to_seconds(pb_time) == time_to_seconds(now_igt):
                priority = 12
              else:
                priority = 8

            for l in range(len(allname)):
              if allname[l] == nickname:
                if priority == 8 or priority == 12:
                  if world_id in sent_user:
                    print(f'[{logtime}] del world_id from sent_user: {world_id}')
                    del sent_user[world_id]
                    priority = 0
                else:
                  sent_user[world_id] = nickname
                with open(path_temp, 'w', encoding='utf-8') as f:
                  print(f'[{logtime}] send priority: {nickname} : {allname[l+1]}/{priority}')
                  f.write(f'{nickname} : {allname[l+1]}')
                  f.write(f'\n{priority}')
                  break

            # save event id and igt in world id
            sent_world_ids[world_id] = [event_id, max_igt]

        # loop delay
        time.sleep(10)

    except Exception as e:
      # log time
      logtime = datetime.datetime.now()

      # log
      print(f'[{logtime}] an error occurred: {e}. retrying.')
      time.sleep(60)

# Defs
# https://stackoverflow.com/questions/72630298/adding-any-unix-timestamp-in-discord-py
def convert_to_unix_time(date: datetime.datetime, days: int, hours: int, minutes: int, seconds: int) -> str:
  # Get the end date
  end_date = date + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

  # Get a tuple of the date attributes
  date_tuple = (end_date.year, end_date.month, end_date.day, end_date.hour, end_date.minute, end_date.second)

  # Convert to unix time
  return f'<t:{int(time.mktime(datetime.datetime(*date_tuple).timetuple()))}:R>'


# https://gist.github.com/himoatm/e6a189d9c3e3c4398daea7b943a9a55d
def string_to_datetime(string):
  return datetime.datetime.strptime(string, '%M:%S')


def fetch_data():
  url = 'https://paceman.gg/api/ars/liveruns'
  response = requests.get(url)
  if response.status_code == 200:
    return response.json()
  else:
    print(f'Failed to fetch data. Status code: {response.status_code}')
    return None


def convert_to_hh_mm_ss(time):
  if isinstance(time, int):
    time = str(time)

  seconds = int(time[:-3])
  milliseconds = int(time[-3:])
    
  hours = seconds // 3600
  minutes = (seconds % 3600) // 60
  seconds = seconds % 60
    
  if hours > 0:
    return f'{hours:02}:{minutes:02}:{seconds:02}'
  else:
    return f'{minutes:02}:{seconds:02}'


def time_to_seconds(time_str):
  parts = list(map(int, time_str.split(':')))
  if len(parts) == 2:
    return parts[0] * 60 + parts[1]
  elif len(parts) == 3:
    return parts[0] * 3600 + parts[1] * 60 + parts[2]
  return 0


def getallnames(path, path_dir):
  if not os.path.isdir(path_dir):
    os.makedirs(path_dir)
    
  try:
    with open(path, 'x') as f:
      f.write('')
  except FileExistsError:
    pass
    
  with open(path, 'r') as f:
    name = f.read().splitlines()
        
    list_name_url = []
    for line in name:
      parts = line.split(' : ')
      if len(parts) == 2:
        list_name_url.append(parts[0])
        list_name_url.append(parts[1])
    
  return list_name_url


def get_all_pace(path):
  with open(path, 'r') as f:
    pace = f.read().splitlines()

  result = []
  for line in pace:
    parts = line.split(' : ')
    name = parts[0]
    times = parts[1]

    times_list = re.split(r'\/| ', times)
        
    cleaned_times = [item for item in times_list if re.match(r'^\d{1,2}(:\d{2})?$', item)]
        
    result.extend([name] + cleaned_times)

  return result


if __name__ == '__main__':
  send_priority()