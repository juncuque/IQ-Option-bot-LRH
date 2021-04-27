#!/usr/bin/env python

###############################################################################################################################################

	# Original code at https://github.com/lycanhunt3r/IQ-Option-bot-LRH #
		# Copyright © 2021 by Lycanhunt3r - GPLv3 #
		
###############################################################################################################################################

import logging, json, sys, time, os, configparser, pickle, uuid, base64, random, math, shutil, pstats, io, multiprocessing
import webbrowser, platform, ast, subprocess, threading
import psutil, cryptography, boto3, numba, ciso8601

import numpy as np

from iqoptionapi.stable_api import IQ_Option
from talib.abstract import *
from datetime import datetime
from dateutil import tz
from pythonping import ping
from time import perf_counter
from numba import jit, njit, float32, prange, types
from numba.typed import Dict
from multiprocessing import Process, Value, Array, Pool, Manager
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography import *


logging.disable(level=(logging.DEBUG))

###############################################################################################################################################
		# # # IQ OPTION BOT LRH - v0.6 ALPHA # # #

## ◄ 1 ► VARIABLES 			(ln 45)
## ◄ 2 ► GERAL FUNCTIONS 	(ln 220)
## ◄ 3 ► MENU 				(ln 467)
## ◄ 4 ► RUN BOT 			(ln 1105)
## ◄ 5 ► CATALOGUER 		(ln 1798)
## ◄ 6 ► SIMULATOR 			(ln 2063)
## ◄ 7 ► ANALYZER 			(ln 3055)


# █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ #

# ▓▓▓   # #   ██╗   ██╗ █████╗ ██████╗ ██╗ █████╗ ██████╗ ██╗     ███████╗███████╗
#   ▓   # #   ██║   ██║██╔══██╗██╔══██╗██║██╔══██╗██╔══██╗██║     ██╔════╝██╔════╝
#   ▓   # # # ██║   ██║███████║██████╔╝██║███████║██████╔╝██║     █████╗  ███████╗
#   ▓   # #   ╚██╗ ██╔╝██╔══██║██╔══██╗██║██╔══██║██╔══██╗██║     ██╔══╝  ╚════██║
# ▓▓▓▓▓ # # #  ╚████╔╝ ██║  ██║██║  ██║██║██║  ██║██████╔╝███████╗███████╗███████║
# # # # # #     ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚══════╝
# ----------------------------------------------------------------------------------------------------------------------------- #
		### GENERAL ###

version = 0.5	#0.6 ALPHA

# ----------------------------------------------------------------------------------------------------------------------------- #
		### ACCOUNT ###
current_account = {}

perfil = ''
balance_amount = 0
descricao_perfil = ''

# ----------------------------------------------------------------------------------------------------------------------------- #
		### CONFIG ###

config_id = ''

bot_config = {
	'update_delay_min': 0,											#
	'ping_limit': 500,												#
	'bet_value': 1,											#
	'max_par_bots': 20,												#
	'min_payout': 60,												#
	'balance_loss_limit': -1,		#Bet stopping point in a single run | -1: 'no limits'		#
}

config = {}
def reset_config():
	global config
	config = {
		'name': 'Standard Configuration',								#
		'id': '',														#
		'winrate': [0,0,0],			## [ Total , real , simulation ]		# 
		'total_wins': [0,0,0],		## [ Total , real , simulation ]		#
		'total_bets': [0,0,0],		## [ Total , real , simulation ] 		#
		'total_payout': [0,0],		## [real, simulation]

		'sleep_time': 0.1,												

		'candles_size': 1,
		
		'sma_period': 30,
		'bband_threshold': 0.05,		#Negative = '-threshold' | Positive = '+threshold'
		'bbands_period': 30,
		'bbands_desvio': 2.7,
		
		'power_for_middle': 0,		#Limit to consider the power of movement to still be in "middle" (0 | 1 | 2)
		'mov_sensors': [360,120,42,18,6],			#Melhors ser divisíveis por 3		40 = 1 bloco aos 5min(=1min)
		'watch_sensor_id': 0,

		'segundos_max': 29,												
		'open_bet_seconds': 40,											
		
		'when_hit_top': 'down',				# 'up' \ 'down' \ 'none'
		'when_hit_bot': 'up',			# 'up' \ 'down' \ 'none'
		'reverse_movement': False,
		'reverse_strategy': False,
		'use_mood': True,
		
		'use_only_with_mood': True,
		'use_reverse_mood': False,
		'use_mood_with_rend': False,
		'mood_threshold_min': 30,
		'mood_threshold_max': 100
	}

configs = {}

#SIMULATOR
simulator_config = {
	'mode': 'single-config',		# multi-configs / single-config
	'rend': 90,
	'catalogue': 'none',
	'mconfiguration': 'Standard MConfig',
	'status': 'TO-BUILD',
	'cores': max(1,multiprocessing.cpu_count() - 1)}

# ----------------------------------------------------------------------------------------------------------------------------- #
		### STATS ###

bot_stats = {}
def reset_bot_stats(real=True):
	global bot_stats, pars
	pars = []
	if real:
		ping_iq = ping('iqoption.com').rtt_avg_ms
	else:
		ping_iq = 0
	bot_stats = {'ping': ping_iq ,
			'total_points': 0 ,
			'saved_points': 0 ,
			'errors': 0 ,
			'online': 0 ,
			'min_for_update': bot_config['update_delay_min'],
			'need_update': True,
			'update_ping': False,
			'check_showscreen': True,
			'hour': '00000',
			'minuto': -1,
			'wdl': [0, 0, 0],
			'winrate': 0,
			'total_payout': 0,
			'total_bets': 0,
			'bets_last': 0,
			'bets_per_min': 0,
			'bets_last_minute': -1,
			'total_minutes': 0,
			'total_combo_history': [0, 0],
			'first_time_run': True}

simulator = {}
def reset_simulator():
	global simulator
	simulator = {
		'pars_list': [],
		'in_bet': False,
		'bet_list': {},				#{ name: {time, seconds, bbands, tide, result} }
		'configs': [],
		'configs_results': {},		#[bot_stats, config]
		'config_progress': [0,0],
		'file_progress': [0,0],
		'entries_progress': [0,0],
		'total_payout': 0,
		'show_delay': 0,
		'multi_simulation': {},
		'cache': { 'bbands': [], 'sma': [], 'tide': [], 'values': []}
		}

# ----------------------------------------------------------------------------------------------------------------------------- #
		### PARS ###

pars = []
def new_par(paridade):
	par = {'name': paridade[2] ,
		'rendimento': int(paridade[0]),
		'sma': 0 ,
		'direcao': 'none' ,
		'last_sma': 0 ,
		'last_bbands': 0.5 ,
		'last_second': -1 ,
		'mar': list(global_mar) ,
		'tide_power': 0,
		'total_tide': [0] * len(config['mov_sensors']),
		'movimento': '' ,
		'valor': 0 ,
		'arrow': 'middle' ,
		'status': 'OK' ,				# 'OK' | 'OFF' | 'LOCK' | 'LAG' | 'WAIT'
		'bet': 0 ,
		'bet_id': 0,
		'bet_min': 0 ,
		'bet_type': '',					# 'LOW' | 'HIGH'
		'bet_last_result': '',
		'winrate': 0,
		'combo': 0,
		'combo_history': [0, 0],
		'last_combo': -1,
		'attempt': 0 ,				#TEMP
		'attempt_status': '' ,		#TEMP
		'wdl': [0, 0, 0] ,
		'lucro': 0,
		'mood': -1,
		'valores': {}
		}
	return par


# █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ #

# ▓▓▓▓▓ # #    ██████╗ ███████╗██████╗  █████╗ ██╗         ███████╗██╗   ██╗███╗   ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗███████╗
#    ▓▓ # #   ██╔════╝ ██╔════╝██╔══██╗██╔══██╗██║         ██╔════╝██║   ██║████╗  ██║██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║██╔════╝
# ▓▓▓▓▓ # # # ██║  ███╗█████╗  ██████╔╝███████║██║         █████╗  ██║   ██║██╔██╗ ██║██║        ██║   ██║██║   ██║██╔██╗ ██║███████╗
# ▓▓    # #   ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║         ██╔══╝  ██║   ██║██║╚██╗██║██║        ██║   ██║██║   ██║██║╚██╗██║╚════██║
# ▓▓▓▓▓ # # # ╚██████╔╝███████╗██║  ██║██║  ██║███████╗    ██║     ╚██████╔╝██║ ╚████║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║███████║
# # # # # #    ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝    ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝
# ----------------------------------------------------------------------------------------------------------------------------- #
		### GENERAL ###

#PROFILER
def profile(fnc):
    
    """A decorator that uses cProfile to profile a function"""
    
    def inner(*args, **kwargs):
        
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner

#REPEATS A CHAR(c) FOR AN AMOUNT OF TIMES(x)
def add_char(x, c):
	sinal = ''
	if x < 1:
		return sinal
	for i in range(x):
		sinal += c
	return sinal

#SPLITS AN ARRAY (a) INTO EQUAL PARTS BY THE LIMIT OF (n)
def split_array_into_limit(a, n):
	x = 0
	splitted = []
	single = []
	for value in a:
		single.append(value)
		x +=1
		if x == n:
			splitted.append(list(single))
			single.clear()
			x = 0
	if len(single) > 0:
		splitted.append(list(single))
	return splitted

# ----------------------------------------------------------------------------------------------------------------------------- #
		### PAGE ###

#CENTRALIZES TEXT WITH GIVEN SPACE
def center_text(text, space=120):
	center = add_char(int(round((space - len(str(text))-0.1)/2)), ' ')
	final = center + str(text) + center
	if len(final) < space:
		final += ' '
	final = cut_text(final, space)
	return final

def cut_text(text, space):
	final = text
	while len(final) > space:
		final = final[:-1]
	return final

#SEPARATOR
def print_separator(type=1):
	if type == 0:
		print('∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙')
	if type == 1:
		print('-----------------------------------------------------------------------------------------------------------------------')
	elif type == 2:
		print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')

#PRINT TOP MENU INFORMATION
def print_top_menu_info(page, has_separator=True):
	os.system('cls')
	print('LRH IQ OPTION BOT MENU - version: ' + str(version) + center_text('— ' + page + ' —', 46) + '\n' + 
		descricao_perfil + str(balance_amount) + '\t\tACCOUNT: ' + current_account['account_type'])
	if has_separator:
		print_separator(2)
		print('')

#OPTIONS MENU AND INPUT HANDLER 		[button_to_type, phrase_of_command] , can go back , can continue
def create_options_menu(error, array, has_back=True, has_zero=True, back_text='to go back', zero_text='to continue', type_reminder='Type one of the numbers above'):		
	print_separator(2)
	print('')
	new_error = ''
	choices_list = []
	for has in [['\'', back_text, has_back], ['0', zero_text, has_zero]]:
		if has[2]:
			print('    ' + center_text(has[0], 3) + ' - ' + has[1])
			choices_list.append(has[0])
	print('')
	for a in array:
		if a[0] == '' and a[1] == '':
			print('')
		elif a[0] == '':
			print('\t' + str(a[1]))
		else:
			print('    ' + center_text(a[0], 3) + ' - ' + str(a[1]))
			choices_list.append(str(a[0]))
	print('')
	print_separator()
	print(center_text(error, 119))
	print(type_reminder + ': ', end=' ')
	choice = str(input())
	if choice == '\'s':
		os.system('cls')
		exit()
	if 'ANY' not in choices_list:
		if choice not in choices_list:
			new_error = '\t' + choice + ' is not in the list of commands'
	return choice, new_error

# ----------------------------------------------------------------------------------------------------------------------------- #
		### CONVERTER ###

#TIMESTAMP CONVERTER
def time_converter(x):
	hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
	hora = hora.replace(tzinfo=tz.gettz('GMT'))
	return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6]

def fast_time_converter(x):
	return str(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))

#CONVERTS NUMBER TO A STRING WITH LIMITED SPACE BY ADDING SUFIXES
def number_to_limit_str(number, space):
	markers = ['','k','m','b','t','q']
	if number == 0:
		text = add_char(int(round(space/4,0)), '-')
	else:
		text = str(number)
	for x in range(len(markers)):
		if len(text) > space:
			text = str(math.floor(number/(1000**x))) + markers[x]
		else:
			break
	return text

#CONVERTS A NUMBER OF SECONDS TO DAY(d), HOUR(h) AND SECONDS(s)
def time_to_str(time):
	seconds = time%60
	minutes = (time//60)%60
	hours = (time//3600)%24
	days = time//86400
	text = ''
	keys = [days, hours, minutes]
	marks = ['d','h','m']
	for x in range(len(keys)):
		if keys[x] != 0:
			text += str(keys[x]) + marks[x] + ' '
	text += str(seconds) + 's'
	return text

#DELETE OR SUBSTITUTE PROHIBITED CHARACTERES FOR FILE NAMES
def friendly_file_name(text, c=''):
	title = text
	banned_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
	for char in banned_chars:
		title = title.replace(char, c)
	return title

# ----------------------------------------------------------------------------------------------------------------------------- #
		### FILE ###

def check_dir(path, type='dir'):		#'dir' | 'file'	| 'none' (to nothing with it)
	if os.path.exists(path):
		return True
	else:
		if type == 'dir':
			try:
				os.mkdir(path)
			except:
				return False
		elif type == 'file':
			f = open(path,"w")
			f.close()
		return False

def delete_all_files_in_dir(path):
	for root, dirs, files in os.walk(path):
		for file in files:
			os.remove(path + '/' + file)

def load_file(path, info=''):
	if os.path.isfile(path):
		file = open(path, 'rb')
		info = pickle.load(file)
		file.close()
	else:
		save_file(path, info)
	return info

def save_file(path, info):
	file = open(path, 'wb')
	pickle.dump(info, file)
	file.close()

def list_files(path):
	rlist = []
	check_dir(path)
	for root, dirs, files in os.walk(path):
		rlist.extend(files)
	return rlist

def list_dirs(path):
	rlist = []
	for root, dirs, files in os.walk(path):
		for dir in dirs:
			if os.path.isdir(path + dir):
				rlist.append(dir)
	return rlist

#PARSER
def load_parser(path, type='raw'):			#'raw' = only load | 'list' = load variables as a list into a dict
	file = configparser.ConfigParser()
	file.read(path)
	aDict = {}
	if type == 'raw':
		pass				#TEMP
	elif type == 'list':
		for sec in file.sections():
			for var in file[sec]:
				aDict[var] = ast.literal_eval(file.get(sec, var))
	return aDict

def save_parser(path, info, section):
	file = configparser.ConfigParser()
	file[section] = info
	check_dir(path, 'file')
	with open(path, 'w') as configfile:
		file.write(configfile)
	print('saving parser...')
	#time.sleep(3)


# █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ #

# ▓▓▓▓▓ # #   ███╗   ███╗███████╗███╗   ██╗██╗   ██╗
#    ▓▓ # #   ████╗ ████║██╔════╝████╗  ██║██║   ██║
# ▓▓▓▓▓ # # # ██╔████╔██║█████╗  ██╔██╗ ██║██║   ██║
#    ▓▓ # #   ██║╚██╔╝██║██╔══╝  ██║╚██╗██║██║   ██║
# ▓▓▓▓▓ # # # ██║ ╚═╝ ██║███████╗██║ ╚████║╚██████╔╝
# # # # # #   ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ 
# ----------------------------------------------------------------------------------------------------------------------------- #
		### LOGIN ###

def login_accounts():
	global current_account
	accounts = []
	id = 0
	error = ''
	
	dirs = [
		'./data',
		'./data/account',
		'./data/config',
		'./data/saved_entries',
		'./data/simulator',
		'./data/analyzer',
		'./data/simulator/rawtest',
		'./data/simulator/stats',
		'./data/simulator/cache',
		'./data/simulator/multiconfigs',
		'./data/simulator/multiconfigs/configurations',
	]
	for dir in dirs:
		check_dir(dir)
	check_unfinished_dir()
	
	#search for accounts
	for root, dirs, files in os.walk('./data/account'):
		for file in files:
			account_file = open('./data/account/' + file, 'rb')
			account = pickle.load(account_file)
			id += 1
			account['id'] = id
			accounts.append(account)
			account_file.close()
	
	#screen
	while True:
		os.system('cls')
		print(center_text('WELCOME TO LRH\'S BOT!', 119))
		options_array = []
		for account in accounts:
			options_array.append([account['id'], account['perfil']['nickname'] + '\t ( ' + account['perfil']['name'] + ' )'])
		choice, error = create_options_menu(error, options_array, back_text='Quit program', zero_text='*register a new account*', type_reminder='Type one of the numbers above to login')
		if choice == '\'':
			os.system('cls')
			exit()
		
		# # new account
		elif int(choice) == 0:
			new_login_account()
			break
		
		# # connect to existing account
		elif int(choice) <= id and int(choice) > 0:
			current_account = accounts[int(choice)-1]
			print('Trying to login with ' + current_account['perfil']['nickname'] + '...')
			success, info = decrypt_login(current_account)
			if success:
				connect = connect_iqoption(info[0], info[1])
				if connect:
					email = ''
					password = ''
					API.change_balance(current_account['account_type'])
					get_perfil()
					perfil_menu_screen()
					break
			
			# # # decrypting error handler
			else:
				os.system('cls')
				print('\nDecrypting error: An important information on the saved login is wrong or outdated.')
				print('\t- Possible exception: If you are on a different device or changed your hardware recently, it\'s possible that the encryption key was changed, so you will need to add the accounts again.')
				print_separator()
				print('\n 1 - to delete current file \t or \t 2 - to delete all account files \t or \t *ANY_KEY - just continue\n')
				print_separator()
				print('Type one of the numbers above to choose: ')
				r_choice = input()
				if r_choice == '1':
					print('\n[1] Deleting current login information...\t\t\tReason: Outdated Encryption Key')
					time.sleep(2)
					os.remove(current_account['file'])
				elif r_choice == '2':
					print('\n[2] Deleting all login information...\t\t\tReason: Outdated Encryption Key')
					time.sleep(2)
					for account in accounts:
						os.remove(account['file'])
				current_account = {}
				break
	login_accounts()

def new_login_account():
	while True:
		os.system('cls')
		print('Registering new IQ Option account.\t\t\t\t\t\t\t\t\t \' - to go back')
		print_separator()
		if ping('iqoption.com').success:
			print('IQ Option Login\t\t\t Server status: \t ONLINE\n')
			print('Email:   \t', end = ' ')
			email = input()
			if email == '\'':
				break
			elif email == '\'s':
				os.system('cls')
				exit()
			print('Password:\t', end = ' ')
			password = input()
			if password == '\'':
				break
			elif password == '\'s':
				os.system('cls')
				exit()
			print_separator()
			
			connect = connect_iqoption(email, password)
			if connect:
				print_separator()
				print('\nEncrypting and saving your account information...')
				info = {'email': email, 'password': password}
				encrypt_login(info)
				get_perfil()
				perfil_menu_screen()
				break
			else:
				print('Sorry, but your email or password are wrong or doesn\'t exist in IQ Option.')
		else:
			print('IQ Option Login\t\t\t Server status: \t CAN\'T CONNECT')
		print('\n\' - to go back \t or \t 0 - to try again\n\n')
		choice = input()
		if choice == '0':
			continue
		elif choice == '\'':
			break
		else:
			print('\nSorry but ' + choice + ' isn\'t a command')
	return

def connect_iqoption(email, password, show_print=True):
	global API
	if show_print:
		print('Trying to connect...')
	connect = False

	API = IQ_Option(email, password)
	API.connect()

	if API.check_connect():
		if show_print:
			print('\nSuccessfully connected')
		connect = True
	else:
		if show_print:
			print('\nConnection failed')
		time.sleep(3)
	if show_print:
		print('\n')
	return connect

#DECRYPT / ENCRYPT
def take_key():
	rd = random.Random()
	rd.seed(0)
	uid = str(uuid.UUID(int=rd.getrandbits(128))).encode()
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=32,
		salt=b'lycanhunt3r',
		iterations=100000
		)
	chave = base64.urlsafe_b64encode(kdf.derive(uid))
	cadeado = Fernet(chave)
	return cadeado

def encrypt_login(info):
	global current_account
	login = {'account_type': 'PRACTICE'}
	API.change_balance(login['account_type'])
	get_perfil()
	login['perfil'] = {'nickname': perfil['nickname'], 'name': perfil['name'], 'currency': perfil['currency'], 'balance': perfil['balance']}
	login['file'] = './data/account/' + perfil['nickname'] + '.txt'
	key = take_key()
	file = open(login['file'], 'wb')
	for i in ['email', 'password']:
		if i == 'email':
			index = 0
			for x in range(len(info[i])):
				if info[i][-x-1] == '@':
					index = -x-2
					break
			login[i + '_text'] = info[i][0] + add_char(len(info[i]) - 1 - len(info[i][index:]), '*') + info[i][index:]
		else:
			login[i + '_text'] = add_char(len(info[i]), '*')
		login[i] = str(key.encrypt(info[i].encode()).decode())
	pickle.dump(login, file)
	current_account = login
	API.change_balance(current_account['account_type'])
	get_perfil()

def decrypt_login(account):
	info = []
	key = take_key()
	success = True
	try:
		for i in ['email', 'password']:
			info.append(key.decrypt(account[i].encode()))
	except (cryptography.fernet.InvalidToken, TypeError):
		success = False
	return success, info

# ----------------------------------------------------------------------------------------------------------------------------- #
		### CONTROLLERS ###

def get_perfil():
	global perfil, balance_amount, descricao_perfil
	perfil = json.loads(json.dumps(API.get_profile_ansyc()))
	balance_amount = API.get_balance()
	descricao_perfil = 'NAME: ' + perfil['name'] + '  \tNICK: ' + perfil['nickname'] + '  \tBALANCE:  ' + API.get_currency() + ' '

def check_unfinished_dir():
	config_path = './data/unfinished_dirs.txt'
	info = load_file(config_path, [])
	for path in info:
		shutil.rmtree(path)
	save_file(config_path, [])
	
# ----------------------------------------------------------------------------------------------------------------------------- #
		### INFO AND STATS ###

#PERFIL MENU
def perfil_menu_screen():
	load_configuration(take_bot_last_config())
	load_bot_configuration()
	reset_bot_stats()
	error = ''
	while True:
		print_top_menu_info('MENU', has_separator=False)
		options_array = [
			[1, 'Account Information'],
			[2, 'Configuration'],
			[3, 'Cataloguer'],
			[4, 'Simulator'],
			[5, 'Analyzer [UNFINISHED]']
		]
		choice, error = create_options_menu(error, options_array, back_text='Quit and go back to accounts login menu', zero_text='Start bot')
		if choice == '\'':
			break
		elif choice == '0':
			start_bot()
		elif choice == '1':
			account_menu()
		elif choice == '2':
			configuration_menu()
		elif choice == '3':
			cataloguer_menu()
		elif choice == '4':
			simulator_menu()
		elif choice == '5':
			analyzer_menu()

#ACCOUNT MENU
def account_menu():
	error = ''
	options_array = [
		[1, 'Account type: ' + current_account['account_type']],
		['','']]
	
	get_perfil()
	keys = [
		[['Nickname:   \t', perfil['nickname']],
		['Balance:    \t', '(' + perfil['balances'][0]['currency'] + ') ' + str(perfil['currency_char']) + str(perfil['balances'][0]['amount'])]],
		
		[['Email:      \t', perfil['email']],
		['Created at: \t', time_converter(perfil['created'])]],
		
		[['Activated:  \t', perfil['is_activated']],
		['Vip:        \t', perfil['is_vip_group']]],
		
		[['',''],['','']],
		
		[['Account ID: \t', perfil['id']],
		['SKEY:       \t', perfil['skey']]],
		
		[['Balance ID:  \t', perfil['balance_id']],
		['','']],
		
		[['',''],['','']],
		
		[['Name:       \t', perfil['name']],
		['Gender:     \t', perfil['gender']]],
		
		[['Birthdate:  \t', time_converter(perfil['birthdate'])],
		['','']],
		
		[['',''],['','']],
		
		[['Nationality:\t', '(' + perfil['flag'] + ') ' + perfil['nationality']],
		['City:       \t', perfil['city']]],
		
		[['Postal index:\t', perfil['postal_index']],
		['Address:    \t', perfil['address']]],
		
		[['Phone:      \t', perfil['phone']],
		['','']],
		
		[['',''],['','']],
	]

			

	for key in keys:
		if key[0][1] == '':
			options_array.append(['',' ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ ∙ '])
		else:
			options_array.append(['', key[0][0] + str(key[0][1]) + add_char(32-len(str(key[0][1])), ' ') + '\t' + key[1][0] + str(key[1][1])])
	
	options_array.append(['', '\t\t\t\tPRACTICE:   \t(' + perfil['balances'][1]['currency'] + ') ' + str(perfil['balances'][1]['amount'])])
	for x in range(len(perfil['balances'])-2):
		options_array.append(['', '\t\t\t\t' + perfil['balances'][x+2]['currency'] + ':        \t(' + perfil['balances'][x+2]['currency'] + 
			') ' + str(perfil['balances'][x+2]['amount'])])
	
	while True:
		print_top_menu_info('ACCOUNT', False)
		choice, error = create_options_menu(error, options_array, has_zero=False, back_text='Save and go back to menu')
		if choice == '\'':
			break
		elif choice == '1':
			print('You can change your account type to PRATICE or REAL: ')
			confirm = input()
			if confirm == current_account['account_type']:
				error = 'Wanted to change into the same value: ' + confirm + ' to ' + confirm
			else:
				if confirm.lower() == 'real':
					print('Are you sure to change your account to REAL? You\'ll be using real money. [Y - to confirm]')
					response = input()
					if response.lower() == 'y':
						save_current_account('REAL')
						error = 'You changed your account to REAL.'
					else:
						error = 'You didn\'t confirm to change your account to REAL.'
				elif confirm.lower() == 'practice':
					save_current_account('PRACTICE')
					error = 'You changed your account to PRACTICE.'
				else:
					error = 'Sorry, but ' + confirm + ' isn\'t an option.'
				options_array[0] = [1, 'Account type: ' + current_account['account_type']]

def save_current_account(type):
	global current_account
	current_account['account_type'] = type
	API.change_balance(type)
	file = open(current_account['file'], 'wb')
	pickle.dump(current_account, file)
	file.close()
	get_perfil()

# ----------------------------------------------------------------------------------------------------------------------------- #
		### CONFIGURATION ###

def configuration_menu(need_update_config=False):
	global config
	error = ''
	need_update_bot_config = False
	while True:
		print_top_menu_info('CONFIGURATIONS')
		print('\tHere is where you can chance any aspects of how tha bot and program works, as well as save preset to use later and ' +
			'see their stats from simulations and real-life cenarios.\n\tSETTINGS: Boolean needs to be written as "True" or "False", NOT as 1 or 0; ' +
			'Floats have their decimals are market by an dot, "."; Arrays are market by a comma, ",", with NO spaces or brackets; Strings can\'t ' +
			'have commas nor dots.')
		id = 1
		id_for_bot_config = 0
		options_array = []
		commands = []
		for configuration in [bot_config, config]:
			for key in configuration.keys():
				options_array.append([id, add_char(18-len(key), ' ') + key + ': ' +  cut_text(str(configuration[key]), 89)])
				id += 1
				commands.append(key)
			options_array.append(['',''])
			if configuration == bot_config:
				id_for_bot_config = id
		choice, error = create_options_menu(error, options_array, back_text='Go back to menu', zero_text='Check list of saved configurations')
		if choice == '\'':
			break
		elif choice == '0':
			error = check_list_config()
		elif choice != 'ERROR':
			choice = int(choice)
			print('\n' + commands[int(choice)-1] + ' new value: ')
			new_value = input()
			if new_value == 'False' or new_value == 'True':
					if new_value == 'False':
						new_value = False
					else:
						new_value = True
					
			else:
				if '.' in new_value:
					new_value = float(new_value)
				elif ',' in new_value:
					new_value = str.split(',')
				else:
					isnt_string = True
					for letter in ['a','b','c','d','e','f','g','h','i','j','l','m','n','o','p','q','r','s','t','u','v','x','z','k','y','w']:
						if letter in new_value:
							isnt_string = False
							break
					if isnt_string:
						new_value = int(new_value)
			if choice < id_for_bot_config:
				if bot_config[commands[choice-1]] != new_value:
					bot_config[commands[choice-1]] = new_value
					need_update_bot_config = True
				else:
					error = 'Same value, from ' + str(bot_config[commands[choice-1]]) + ' to ' + str(new_value)
			else:
				if config[commands[choice-1]] != new_value:
					config[commands[choice-1]] = new_value
					need_update_config = True
				else:
					error = 'Same value, from ' + str(config[commands[choice-1]]) + ' to ' + str(new_value)
				config[commands[choice-1]] = new_value
	if need_update_bot_config:
		save_bot_configuration()
	if need_update_config:
		need_name = True
		for root, dirs, files in os.walk('./data/config'):
			current_id = calculate_config_id()
			for file in files:
				config_file = open('./data/config/' + file, 'rb')
				c = pickle.load(config_file)
				if c['id'] == current_id:
					need_name = False
					break
				config_file.close()
		if need_name:
			print('\nDo you want to give this configuration a name? Just enter if not...  ')
			escolha = input()
			if escolha == '':
				config['name'] = config['id']
			else:
				config['name'] = escolha
			for con in ['winrate', 'total_wins', 'total_bets']:
				config[con] = [0,0,0]
			save_configuration()
		path = './data/bot_last_config.txt'
		file = open(path, 'w')
		file.write(config['id'])
		file.close()

def check_list_config():
	configurations = []
	id = 0
	error = ''
	
	#search for configurations
	print_top_menu_info('CONFIGURATIONS: list of configs')
	print('Loading list of configurations...') 
	for root, dirs, files in os.walk('./data/config'):
		for file in files:
			id += 1
			config_file = open('./data/config/' + file, 'rb')
			c = pickle.load(config_file)
			
			if c['total_bets'][0] == 0:
				winrate_total = 0
			else:
				winrate_total = abs(c['winrate'][0]-50)/(5000/min(c['total_bets'][0], 5000))
			
			if c['total_bets'][1] == 0:
				winrate_real = 0
			else:
				winrate_real = abs(c['winrate'][1]-50)/(1000/min(c['total_bets'][1], 5000))
			
			to_append = [winrate_total,
				winrate_real,
				c['winrate'][1], c['total_bets'][1],
				c['winrate'][0], c['total_bets'][0],
				c['winrate'][2], c['total_bets'][2],
				c['name'], c['id'], '']
			if c['id'] == config['id']:
				to_append[10] = ' [CURRENT]'
			configurations.append(to_append)
			config_file.close()
			print(c['name'] + ' loaded.')
	print('Loading done, creating list...')
	configurations = sorted(configurations, reverse=True)
	
	options_array = []
	for conf in configurations:
		options_array.append([configurations.index(conf)+1, 'WINRATE = ' + str(conf[4]) + '% (' + str(conf[2]) + '%|' + str(conf[6]) + '%)\t  ' +
			'TOTAL BETS = ' + number_to_limit_str(conf[5], 4) + ' (' + number_to_limit_str(conf[3], 4) + '|' + number_to_limit_str(conf[7], 4) + 
			')\t:' + cut_text(conf[8], 35) + conf[10]])

	while True:
		look_for = 404040
		print_top_menu_info('CONFIGURATIONS: list of configs')
		print('\t\t\tDATA: total ( real | simulation )')
		choice, error = create_options_menu(error, options_array, has_zero=False, back_text='Go back to menu')
		if choice == '\'':
			break
		elif int(choice) <= id and int(choice) >= 0:
			look_for = int(choice)-1
		elif int(choice) < -id:
			look_for = int(choice)
		if look_for != 404040:
			if configurations[look_for][10] != ' [CURRENT]':
				load_configuration(configurations[look_for][9])
				path = './data/bot_last_config.txt'
				with open(path, 'w') as file:
					file.write(config['id'])
				error = 'Changed to new config: ' + config['name']
				break
			else:
				error = 'Can\'t change to the config being already used: ' + config['name']
	return error

#CALCULATIONS
def int_to_alphabet(id):
	parts = id.split('-')[::-1]
	encoding = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
		'a', 'b', 'c', 'd', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
		'A', 'B', 'C', 'D', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
		'!', '@', '#', '$', '%', '¨', '&', '=', '+', '.', ',', '~', '^', '´', '`', '(', ')', '[', ']', '{', '}', ';']
	text = ''
	for part in parts:
		full_number = int(part)
		while full_number > 0:
			number = full_number % len(encoding)
			full_number = full_number // len(encoding)
			text = encoding[number] + text
		text = '-' + text
	text = text[1:]
	return text

def calculate_config_id():
	global config
	id = ''
	keys = [
		'sleep_time',
		'segundos_max',
		'open_bet_seconds',
		
		'candles_size',
		'sma_period',
		'bband_threshold',
		'bbands_period',
		'bbands_desvio',
		
		'power_for_middle',
		'mov_sensors',
		'watch_sensor_id',

		'when_hit_top',
		'when_hit_bot',
		'reverse_movement',
		'reverse_strategy',
		'use_mood',
		
		'use_only_with_mood',
		'use_reverse_mood',
		'use_mood_with_rend',
		'mood_threshold_min',
		'mood_threshold_max'
	]
	for key in keys:
		if isinstance(config[key], bool):
			if config[key]:
				add = '1'
			else:
				add = '0'
		else:
			add = str(int(str(config[key]).encode().hex(), 16))
		id += add
	id = int_to_alphabet(id[:-1])
	config['id'] = id
	return id

def take_bot_last_config():
	path = './data/bot_last_config.txt'
	if os.path.isfile(path):
		file = open(path, 'r')
		config_id = file.read()
	else:
		config_id = calculate_config_id()
		file = open(path, 'w')
		file.write(config_id)
		file.close()
		save_configuration()
		file = open('./data/config/' + config_id + '.txt', 'wb')
		pickle.dump(config, file)
	file.close()
	return config_id

#FILE HANDLERS
def save_configuration():
	path = './data/config/' + config['id'] + '.txt'
	file = open(path, 'wb')
	pickle.dump(config, file)
	file.close()

def load_configuration(config_id):
	global config
	path = './data/config/' + config_id + '.txt'
	if os.path.isfile(path):
		config_file = open(path, 'rb')
		config = pickle.load(config_file)
		config_file.close()
		if 'total_payout' not in config:
			config['total_payout'] = [0,0]
			save_configuration()
	else:
		save_configuration()

def save_bot_configuration():
	path = './data/bot_configuration.txt'
	file = open(path, 'wb')
	pickle.dump(bot_config, file)
	file.close()

def load_bot_configuration():
	global bot_config
	path = './data/bot_configuration.txt'
	if os.path.isfile(path):
		config_file = open(path, 'rb')
		bot_config = pickle.load(config_file)
		config_file.close()
	else:
		save_bot_configuration()


# █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ #

# ▓▓ ▓▓ # #   ██████╗ ██╗   ██╗███╗   ██╗    ██████╗  ██████╗ ████████╗
# ▓▓ ▓▓ # #   ██╔══██╗██║   ██║████╗  ██║    ██╔══██╗██╔═══██╗╚══██╔══╝
# ▓▓▓▓▓ # # # ██████╔╝██║   ██║██╔██╗ ██║    ██████╔╝██║   ██║   ██║   
#    ▓▓ # #   ██╔══██╗██║   ██║██║╚██╗██║    ██╔══██╗██║   ██║   ██║   
#    ▓▓ # # # ██║  ██║╚██████╔╝██║ ╚████║    ██████╔╝╚██████╔╝   ██║   
# # # # # #   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚═════╝  ╚═════╝    ╚═╝   
# ----------------------------------------------------------------------------------------------------------------------------- #
		### PARS ###

#CHECK IF THERE ARE DUPLICATED PARS, DELETING THE EXTRA'S ONES.
def clean_pars_pos():
	global pars, bot_stats
	
	remove_list = []
	number = 0
	
	for n in range(len(list(pars))):
		#check duplicates
		nome = pars[n]['name']
		aparições = 0
		for p in pars:
			if nome == p['name']:
				aparições += 1
		while aparições > 1:
			remove_list.append(nome)
			aparições -= 1
		#check actives
		if pars[n]['status'] == 'OK':
			number += 1
		#reorder OFF and LOCK to bottom
		elif pars[n]['status'] == 'LOCK' or pars[n]['status'] == 'OFF':
			pars.append(pars[n])
			pars.remove(pars[n])
			n -= 1
	bot_stats['online'] = number
	
	if len(remove_list) > 0:
		for r in pars:
			if remove_list.count(r['name']) > 0:
				remove_list.remove(r['name'])
				pars.remove(r)

#COUNT HOW MANY PARS ARE ACTIVE				#UNUSED
def active_pars():
	global bot_stats
	
	number = 0
	
	for x in range(len(pars)):
		if pars[x]['status'] == 'OK' or pars[x]['status'] == 'LAG':
			number += 1
	bot_stats['online'] = number
	return number

#SEARCH FOR PARS ON IQ OPTION'S SERVERS
def search_pars():
	global pars, bot_stats
	
	tipo_par = ['turbo']

	par_list = []
	need_update_active = False
	par_all = API.get_all_open_time(type_to_get=tipo_par)	#LRH: 'all': all | 'binaries': turbo/binary | 'other': (cfd, forex, crypto)
	pay_all = API.get_all_profit(type_to_get=tipo_par)		#LRH: 'turbo' | 'binary' | 'all' or 'binaries'
	
	for tipo in tipo_par:		#['turbo', 'binary']
		for paridade in par_all[tipo]:
			is_in_pars = False
			is_open = par_all[tipo][paridade]['open']
			if is_open:
				if isinstance(pay_all[paridade][tipo], int) or isinstance(pay_all[paridade][tipo], float):
					pay = int(100 * pay_all[paridade][tipo])
				else:
					pay = -1
			if bot_stats['first_time_run'] == False:
				for par in pars:
					if par['name'] == paridade:
						is_in_pars = True
						if is_open == False and par['status'] != 'OFF':
							par['status'] = 'OFF'
							par['rendimento'] = 0
							need_update_active = True
							print(par['name'] + ' is closed now.')
							if sum(par['wdl']) > 0 or par['bet'] != 0: 
								pars.append(par)
							pars.remove(par)
							par['mar'] = global_mar
							par['arrow'] = 'middle'
						elif is_open:
							if pay < bot_config['min_payout']:
								par['status'] = 'LOCK'
								need_update_active = True
							else:
								par['status'] = 'WAIT'
								par_list.append([str(pay), par['status'], paridade])
							if pay != -1:
								par['rendimento'] = pay
						break
			if is_in_pars == False and is_open:
				print(paridade + ' [' + str(pay) + '%]')
				if pay >= bot_config['min_payout']:
					par_list.append([str(pay), 'AAA_NEW', paridade])
	
	par_list = sorted(par_list, reverse=True)
	print('\n')
	x = min(bot_config['max_par_bots'], len(par_list))
	if x > 0:
		for i in range(x):
			can_put = True
			if bot_stats['first_time_run'] == False:
				for p in range(len(pars)):
					if pars[p]['name'] == par_list[i][2]:
						if pars[p]['status'] == 'WAIT':
							pars[p]['status'] = 'OK'
							need_update_active = True
						can_put = False
						break
			if can_put:
				need_update_active = True
				add_par_to_list(new_par(par_list[i]))
	if need_update_active:
		clean_pars_pos()
	
	if len(par_list) < 1:
		print('No servers online, trying again in 1 minute..')
		time.sleep(60)
		show_screen()
		search_pars()

#ADD A NEW 'PAR' IN 'PARS'
def add_par_to_list(new_p):
	global pars
	
	pars.append(new_p)
	API.start_mood_stream(pars[-1]['name'])
	API.start_candles_stream(pars[-1]['name'], config['candles_size'], config['sma_period']+1)
	print('New PAR added: ' + pars[-1]['name'] + ' \t rend = ' + str(pars[-1]['rendimento']) + '%  \t [TURBO]')

#STOP THE PARS' STREAMS
def stop_par_streams():
		
	for par in pars:
		API.stop_mood_stream(par['name'])
		API.stop_candles_stream(par['name'])

# ----------------------------------------------------------------------------------------------------------------------------- #
		### CALCULATIONS ###

#GLOBALS VALUES
global_tide = []
global_mar = []
global_keys = [['open', 'open'], ['high', 'max'], ['low', 'min'], ['close', 'close'], ['volume', 'volume'], ['from', 'from']]
global_valores = {}
for key in global_keys: global_valores[key[0]] = np.array([])

def set_globals_onda():
	global global_tide, global_mar
	global_tide = [0] * len(config['mov_sensors'])
	global_mar = [0] * sorted(config['mov_sensors'])[-1]

#TRANSFORM CANDLES INTO VALUES
def get_valores(par, velas):
	global bot_stats

	valores = dict(global_valores)
	for x in list(velas):
		for i in global_keys:
			if velas[x].get(i[1]) is None:
				return False, 0
			else:
				valores[i[0]] = np.append(valores['open'], velas[x][i[1]])
	return True, valores

#CALCULATES THE POWER OF THE WAVE WITHIN AN ARRAY AND DIRECTION
def calc_onda(direction, par, real):
	global pars
	
	tide = list(global_tide)
	
	for mov in range(len(config['mov_sensors'])):
		power_pop = pars[par]['mar'][-config['mov_sensors'][mov]]
		pars[par]['total_tide'][mov] = pars[par]['total_tide'][mov] + (direction - power_pop)
		tide[mov] = max(min(pars[par]['total_tide'][mov]*3/config['mov_sensors'][mov],3),-3)
	pars[par]['mar'].pop(0)
	pars[par]['mar'].append(direction)
	pars[par]['tide_power'] = tide
	
	watch = config['watch_sensor_id']
	# movimento
	if real:
		if tide[watch] > 0:
			pars[par]['movimento'] = 'CIMA ' + add_char(math.ceil(tide[watch]), '▲')
		elif tide[watch] < 0:
			pars[par]['movimento'] = 'BAIX ' + add_char(abs(math.floor(tide[watch])), '▼')
		else:
			pars[par]['movimento'] = 'MEIO    '
	
	#seta
	if tide[watch] > config['power_for_middle']:
		pars[par]['arrow'] = 'up'
	elif tide[watch] < -config['power_for_middle']:
		pars[par]['arrow'] = 'down'
	else:
		pars[par]['arrow'] = 'middle'

def get_stream_velas(par):
	sucesso = False
	if pars[par]['status'] == 'OK' or pars[par]['bet'] != 0 or pars[par]['status'] == 'LAG':
		velas = API.get_realtime_candles(pars[par]['name'], config['candles_size'])
		sucesso, valores = get_valores(par, velas)
	else:
		valores = 0
	return sucesso, valores

#MAIN PAR CONTROLLER
#@profile
def runbot(par, valores, real=True):
	global bot_stats, pars
	
	#Calculo de indicadores
	
		#bbands_b
	b_up, b_mid, b_low = BBANDS(valores, config['bbands_period'], config['bbands_desvio'], config['bbands_desvio'], 0)

	price = float(valores['close'][-1])-float(b_low[-1])
	high = float(b_up[-1])-float(b_low[-1])
	if high == 0:
		bbands = 0.54321		#Valor de erro
	else:
		bbands = round(price/high, 6)

		#sma
	sma = round(float(SMA(valores, config['sma_period'], price='close')[-1]), 6)

		#direção
	if sma > pars[par]['sma']:
		direcao = 1		#'up'
	elif sma < pars[par]['sma']:
		direcao = -1	#'down'
	else:
		direcao = 0		#'middle'

	#Update
	pars[par]['sma'] = sma
	
	if real:
		tempo = time_converter(valores['from'][-1])
	else:
		tempo = str(datetime.utcfromtimestamp(valores['from'][-1]).strftime('%Y-%m-%d %H:%M:%S'))
	segundos = int(tempo[-2:])
	
	if pars[par]['last_sma'] != sma or pars[par]['last_bbands'] != bbands or segundos != pars[par]['last_second']:
		if segundos != pars[par]['last_second']:
			calc_onda(direcao, par, real)
		pars[par]['last_second'] = segundos
		pars[par]['last_sma'] = sma
		pars[par]['last_bbands'] = bbands
		pars[par]['valor'] = valores['close'][-1]
		
		bot_stats['hour'] = tempo
		bot_stats['minuto'] = int(tempo[-5:][:-3])
		
		check_bet(par, real)
		if real:
			bot_stats['check_showscreen'] = True
			calc_mood(par)
			bot_stats['saved_points'] += 1
	bot_stats['total_points'] += 1

#CALCULATES PAR'S MOOD
def calc_mood(par):
	global pars
	mood = int(round(API.get_traders_mood(pars[par]['name']), 2)*100)
	pars[par]['mood'] = mood

# ----------------------------------------------------------------------------------------------------------------------------- #
		### BET SYSTEM ###

#CHECK IF BET IS POSSIBLE AND CHANGES PAR'S STATUS
def check_bet(par, real):
	global pars, bot_stats

	if pars[par]['bet'] != 0 and pars[par]['bet_min'] != bot_stats['minuto'] and pars[par]['last_second'] < 2:
		check_results_bet(par, real)
	elif real and pars[par]['last_second'] > config['segundos_max'] and pars[par]['last_second'] < config['open_bet_seconds']:
		if bot_stats['ping'] < bot_config['ping_limit'] and pars[par]['status'] == 'LAG':
			pars[par]['status'] = 'OK'
	elif pars[par]['bet'] == 0 and bot_stats['ping'] < bot_config['ping_limit']:
		pars[par]['status'] = 'OK'
		bet_click(par, real)
	elif real and bot_stats['ping'] >= bot_config['ping_limit']:
		pars[par]['status'] = 'LAG'
		bot_stats['update_ping'] = True

#ATIVATES BET, USING THE CURRENT CONFIGURATION
def bet_click(par, real):		#sinal = 1: 'acima' | -1: 'abaixo'
	global pars, bot_stats

	#trigger
	if pars[par]['arrow'] == config['when_hit_top'] and pars[par]['last_bbands'] < config['bband_threshold']:
		sinal = 1
	elif pars[par]['arrow'] == config['when_hit_bot'] and pars[par]['last_bbands'] > (1-config['bband_threshold']):
		sinal = -1
	else:
		return

	#strategies
	if config['reverse_movement']:
		sinal = sinal * -1
	if real and config['use_mood']:
		sinal = mood_strategy(par, sinal)
	if config['reverse_strategy']:
		sinal = sinal * -1
	
	#bet
	if bot_config['balance_loss_limit'] == -1 or (-bot_config['balance_loss_limit']) < (bot_stats['total_payout'] - bot_config['bet_value']):
		if sinal == 1:
			if real: 
				status,id = API.buy(bot_config['bet_value'], pars[par]['name'], 'call', 1)
				print('BET HIGH')
			pars[par]['bet_type'] = 'HIGH'
		elif sinal == -1:
			if real: 
				status,id = API.buy(bot_config['bet_value'], pars[par]['name'], 'put', 1)
				print('BET LOW')
			pars[par]['bet_type'] = 'LOW'
		else:
			status = False
		
		if real == False:
			status = True
			id = -1
		
		if status:
			pars[par]['bet_id'] = id
			minuto = bot_stats['minuto']
			if pars[par]['last_second'] > config['open_bet_seconds']:
				minuto += 1
			pars[par]['bet_min'] = minuto
			pars[par]['bet'] = pars[par]['valor']
			
			bot_stats['total_bets'] += 1

def mood_strategy(par, sinal):
	sinal_mood = sinal
	
	mood = pars[par]['mood']
	if sinal == -1:
		mood = 100-mood
	
	rend = 0
	if config['use_mood_with_rend']:
		rend = (100 - pars[par]['rendimento'])
		mood -= rend
	
	if config['mood_threshold_min'] <= mood and mood < config['mood_threshold_max'] - rend:
		if config['use_reverse_mood']:
			sinal_mood = sinal_mood * -1
	elif config['use_only_with_mood']:
		sinal_mood = 0
	
	return sinal_mood

#CHECK RESULTS OF A PREVIOUS BET
def check_results_bet(par, real):
	global pars, bot_stats, config

	config_update_stats = [0]
	
	if real:
		success, lucro = API.check_win_v4(pars[par]['bet_id'])
		if success:
			if lucro is None:
				return
			pars[par]['lucro'] = round(pars[par]['lucro'] + lucro, 2)
			config['total_payout'][0] = round(config['total_payout'][0] + lucro, 2)
			config_update_stats.append(1)
	else:
		sinal = 1
		if pars[par]['bet_type'] == 'LOW':
			sinal = -1
		if pars[par]['valor']*sinal > pars[par]['bet']*sinal:
			lucro = 1
		elif pars[par]['valor'] == pars[par]['bet']:
			lucro = 0
		else:
			lucro = -1
		config_update_stats.append(2)
		success = True
	
	if success:
		if lucro > 0:
			update_wdl(par, 0)
			pars[par]['bet_last_result'] = 'WIN'
			for i in config_update_stats:
				config['total_wins'][i] += 1
				config['total_bets'][i] += 1
				if config['total_bets'][i] != 0:
					config['winrate'][i] = round((config['total_wins'][i]/config['total_bets'][i])*100, 2)
		elif lucro == 0:
			update_wdl(par, 1)
			pars[par]['bet_last_result'] = 'DRAW'
		else:
			update_wdl(par, 2)
			pars[par]['bet_last_result'] = 'LOSS'
			for i in config_update_stats:
				config['total_bets'][i] += 1
				if config['total_bets'][i] != 0:
					config['winrate'][i] = round((config['total_wins'][i]/config['total_bets'][i])*100, 2)
		
		#clean-up
		pars[par]['bet_status'] = ''
		pars[par]['bet'] = 0
		pars[par]['bet_id'] = 0
		pars[par]['bet_min'] = -1

#UPDATE WDL AND CHANGES COMBO
def update_wdl(par, result):
	global pars, bot_stats

	pars[par]['wdl'][result] += 1
	bot_stats['wdl'][result] += 1
	if result != 1:
		check_combo(par, min(1, result))
	
	#winrate
	for stat in [pars[par], bot_stats]:
		winrate = int(round((stat['wdl'][0]/max(stat['wdl'][0] + stat['wdl'][2],1))*100, 0))
		stat['winrate'] = winrate
	
def check_combo(par, result):
	global pars, bot_stats

	if result == pars[par]['last_combo']:
		pars[par]['combo'] += 1
	else:
		pars[par]['combo'] = 1
		pars[par]['last_combo'] = result
	
	if pars[par]['combo_history'][result] < pars[par]['combo']:
			pars[par]['combo_history'][result] = pars[par]['combo']
			if bot_stats['total_combo_history'][result] < pars[par]['combo']:
				bot_stats['total_combo_history'][result] = pars[par]['combo']

# ----------------------------------------------------------------------------------------------------------------------------- #
		### SHOW TABLE ###

#UPDATE BOT_STATS
	#banca
def update_balance():
	global balance_amount
	balance_amount = API.get_balance()

	#Delay
def renew_bot_delay():
	global bot_stats
	bot_stats['need_update'] = False

	#Bets/m
def check_bets_per_min():
	global bot_stats
	if bot_stats['bets_last_minute'] != bot_stats['minuto']:
		bot_stats['bets_last_minute'] = bot_stats['minuto']
		before = bot_stats['total_bets'] - bot_stats['bets_last']
		bot_stats['bets_per_min'] = (bot_stats['bets_per_min']*bot_stats['total_minutes'] + before)/(bot_stats['total_minutes']+1)
		bot_stats['bets_last'] = bot_stats['total_bets']
		bot_stats['total_minutes'] += 1
		if bot_stats['min_for_update'] <= 0:
			bot_stats['need_update'] = True
			bot_stats['min_for_update'] = bot_config['update_delay_min']
		else:
			bot_stats['min_for_update'] -= 1

#CMD
def show_screen():
	global bot_stats

	#Preload
	screens = []
	
		# pars
	bot_stats['total_payout'] = 0
	for par in pars:
		screen = get_par_stats_str(par)
		screens.append(screen)
	
		# show
	os.system('cls')
	print(get_head_text_str())
	print_separator()
	print('    NAME    | REND |    TIDE\t| MOOD\t|     VALUE\t|      BET \t|    PROFIT\t|   W/D/L   | WINRATE | COMBO')
	print_separator()
	for s in screens:
		print(s)
	print_separator()
	print(get_total_stats_str())

#HEAD TEXT
def get_head_text_str():
	text_head = ('IQ OPTION BOT LRH \t[' + 
		bot_stats['hour'] + 
		'] \t ping: ' + str(bot_stats['ping']) + 
		'\tentries: ' + number_to_limit_str(bot_stats['total_points'],5) + ' (' + number_to_limit_str(bot_stats['saved_points'],5) + 
		')\tActive minutes: ' + str(bot_stats['total_minutes']-1))
	
	text_stats = (descricao_perfil + str(balance_amount) + 
		'\t\tBOTS_ONLINE: ' + str(bot_stats['online']) + '\\' + str(bot_config['max_par_bots']) + 
		'   bets: ' + number_to_limit_str(bot_stats['total_bets'],4))
	return (text_head + '\n' + text_stats)

#PAR TEXT
def get_par_stats_str(par):
	global bot_stats, pars

	rend = str(par['rendimento']) + ' %'
	if par['rendimento'] < 10:
		rend = ' ' + rend
	
	movimento = par['movimento']
	valor = str(par['valor'])
	
	
	if par['lucro'] > 0:
		lucro = ' +' + number_to_limit_str(par['lucro'], 10)
	else:
		lucro = ' ' + number_to_limit_str(par['lucro'], 10)

	bet = str(par['bet']) + ' ' + par['bet_type']
	if par['status'] != 'OK' and par['status'] != 'LAG':
		bet = str(par['status'])
		movimento = '- - - - '
		valor = ' - - - '
		if par['status'] == 'OFF':
			rend = '- - '
	elif par['bet'] == 0:
		if int(bot_stats['hour'][-2:]) > config['segundos_max'] and int(bot_stats['hour'][-2:]) < config['open_bet_seconds']:
			bet = 'XXX'
		else:
			bet = '---'
	
	wdl_mirror = ['-','-','-']
	wdl = ''
	for r in range(3):
		score = int(par['wdl'][r])
		if score > 0:
			wdl_mirror[r] = number_to_limit_str(score, 3)
	wdl = center_text((wdl_mirror[0] + '/' + wdl_mirror[1] + '/' + wdl_mirror[2]), 11)

	mood = par['mood']
	if mood < 50:
		mood = ' ' + str(100-mood) + '% ▼'
		if mood == ' 100% ▼':
			mood = '100% ▼'
	elif mood > 50:
		mood = ' ' + str(mood) + '% ▲'
		if mood == ' 100% ▲':
			mood = '100% ▲'
	else:
		mood = ' 50% ■'
	
	
	winrate = par['winrate']
	if winrate > 9:
		winrate = str(winrate)
	elif par['wdl'][2] > 0:
		winrate = ' ' + str(winrate)
	else:
		winrate = '--'
	winrate = center_text(winrate+'%', 5)


	#
	screen = (center_text(par['name'], 12) + 
		'| ' + center_text(rend, 5) +
		'|   ' + movimento + 
		'\t|' + mood +
		'\t|    ' + valor + 
		'\t|' + center_text(bet, 15) + 
		'| ' + center_text(lucro, 12) + 
		'\t|' + wdl + 
		'|  ' + str(winrate) +
		'  | ' + center_text(str(par['combo_history'][0]) + '/' + str(par['combo_history'][1]), 5)
		)

	
	
	bot_stats['total_payout'] += round(par['lucro'], 2)
	
	return screen

#TOTAL TEXT
def get_total_stats_str():
	botwdl_mirror = ['-','-','-']
	botwdl = ''
	for r in range(3):
		score = int(bot_stats['wdl'][r])
		if score > 0:
			botwdl_mirror[r] = number_to_limit_str(score, 3)
	botwdl = center_text((botwdl_mirror[0] + '/' + botwdl_mirror[1] + '/' + botwdl_mirror[2]), 11)
	
	winrate = bot_stats['winrate']
	if winrate > 9:
		winrate = str(winrate)
	elif bot_stats['wdl'][2] > 0:
		winrate = ' ' + str(winrate)
	else:
		winrate = '--'
	winrate = center_text(winrate+'%', 5)
	
	total_lucro = round(bot_stats['total_payout'], 2)
	if bot_stats['total_payout'] == 0:
		total_lucro = ' 0'
	elif bot_stats['total_payout'] > 0:
		total_lucro = '+' + str(total_lucro)
	
	#
	total = ('   TOTAL:   |      | ' + 
		' \t\t| \t| \t\t| ' + 
		center_text('Bet/hr: ' + str(int(round(bot_stats['bets_per_min']*60, 0))), 12) + 
		'\t| ' + center_text(total_lucro, 12) + 
		'\t|' + botwdl + 
		'|  ' + winrate +
		'  | ' + center_text((str(bot_stats['total_combo_history'][0]) + '/' + str(bot_stats['total_combo_history'][1])), 5)
		)
	
	return total

# ----------------------------------------------------------------------------------------------------------------------------- #
		### START BOT ###

def start_bot():
	global bot_stats
	set_globals_onda()

	reset_bot_stats()
	os.system('cls')
	print('Searching for PARS..')
	
	#SEARCH PARS
	while True: 
		search_pars()
		if bot_stats['online'] > 0:
			print('\nFound ' + str(bot_stats['online']) + ' PARS:\n')
			break
		print('\nSorry, but were found ' + str(bot_stats['online']) + ' compatible PARS with your configuration.')
		print('\n\t You can change the "min_payout" in configuration to increase the PARS\' range, but it\'ll increase risk.')
		print('\nTRYING AGAIN IN 30 SECONDS..')
		time.sleep(30)
	bot_stats['first_time_run'] = False

	#SHOW TOTAL PARS
	for p in range(len(pars)):
		print(pars[p]['name'] + ' [' + str(pars[p]['rendimento']) + '%]')
	print('\n\nInitializing bot..')
	time.sleep(2)

	#LOOP
	while True:
		for par in range(len(pars)):
			sucesso, valores = get_stream_velas(par)
			if sucesso:
				runbot(par, valores)
		check_bets_per_min()
		if bot_stats['check_showscreen']:
			show_screen()
			bot_stats['check_showscreen'] = False
		
		if bot_stats['update_ping']:
			print('\nUpdating ping..')
			bot_stats['ping'] = ping('iqoption.com').rtt_avg_ms
			bot_stats['update_ping'] = False
		
		if bot_config['balance_loss_limit'] != -1 and -bot_config['balance_loss_limit'] >= (bot_stats['total_payout'] - bot_config['bet_value']):
			print('Balance loss limit has been reached!   [' + str(-bot_config['balance_loss_limit']) + ']\n\tTotal loss: ' + str(bot_stats['total_payout']))
			break
		
		#ANY HEAVY UPDATES
		if bot_stats['need_update'] and int(bot_stats['hour'][-2:]) > config['segundos_max']+1:
			print('\nUpdating ping..')
			bot_stats['ping'] = ping('iqoption.com').rtt_avg_ms
			update_balance()
			print('Updating pars..')
			search_pars()
			save_configuration()
			renew_bot_delay()
			
		time.sleep(config['sleep_time'])
	print('Stopping PARS streams')
	stop_par_streams()
	

# █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ #

# ▓▓▓▓▓ # #    ██████╗ █████╗ ████████╗ █████╗ ██╗      ██████╗  ██████╗ ██╗   ██╗███████╗██████╗ 
# ▓▓    # #   ██╔════╝██╔══██╗╚══██╔══╝██╔══██╗██║     ██╔═══██╗██╔════╝ ██║   ██║██╔════╝██╔══██╗
# ▓▓▓▓▓ # # # ██║     ███████║   ██║   ███████║██║     ██║   ██║██║  ███╗██║   ██║█████╗  ██████╔╝
#    ▓▓ # #   ██║     ██╔══██║   ██║   ██╔══██║██║     ██║   ██║██║   ██║██║   ██║██╔══╝  ██╔══██╗
# ▓▓▓▓▓ # # # ╚██████╗██║  ██║   ██║   ██║  ██║███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗██║  ██║
# # # # # #    ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
# ----------------------------------------------------------------------------------------------------------------------------- #
		### MENU ###

def take_cataloguer_config():
	path = './data/cataloguer_config.txt'
	if os.path.isfile(path):
		file = open(path, 'rb')
		c_config = pickle.load(file)
	else:
		c_config = {'type': 'TURBO', 'pars': 'ALL', 'time': 30, 'time_type': 'DAYS', 'frequency': 1}
		file = open(path, 'wb')
		pickle.dump(c_config, file)
	file.close()
	return c_config

cconfig = {}
def cataloguer_menu():
	global cconfig
	cconfig = take_cataloguer_config()
	error = ''
	config_was_changed = False
	while True:
		print_top_menu_info('CATALOGUER')
		print('The cataloguer is used to take the history of entries at the IQ Option servers according to the selection type.\n')
		
		tempo = cconfig['time_type']
		if cconfig['time'] == 1:
			tempo = tempo[:-1]
		
		options_array = [
			[1, 'Type: \t' + cconfig['type']],
			[2, 'Pars: \t' + cconfig['pars']],
			[3, 'Time: \t' + str(cconfig['time']) + ' ' + tempo],
			[4, 'Frequency: \t' + str(cconfig['frequency'])]
		]
		choice, error = create_options_menu(error, options_array, back_text='Go back to menu', zero_text='Start cataloguer', type_reminder='You can type one of stats to change it\'s configuration')
		if choice == '\'':
			break
		elif choice == '0':
			multiplier = [30617316,2551443,603148,86164,3600,60][['YEARS', 'MONTHS', 'WEEKS', 'DAYS', 'HOURS', 'MINUTES'].index(cconfig['time_type'])]
			entries = max(int(round(cconfig['time'] * (multiplier / cconfig['frequency']), 0)), 1)
			start_cataloguer( entries, cconfig['frequency'], cconfig['type'], ' ' + str(cconfig['time']) + '-' + tempo )
		elif choice == '1':
			error = 'Sorry, setting the "type" isn\'t available at this current version, wait for updates.'
			#change_cataloguer('type', cconfig['type'], 'The type changes what kind of pars it will look for.')
		elif choice == '2':
			error = 'Sorry, setting the "pars" isn\'t available at this current version, wait for updates.'
			#change_cataloguer('pars', cconfig['time'], 'Pars are the specific name of "selections", being able to blacklist or whitelist them.')
		elif choice == '3':
			new_value, config_was_changed = change_cataloguer('time', [cconfig['time'], cconfig['time_type']], 'This changes how much back you want for the cataloguer to reach and save.\n' + 
				' To change the time type follow this values:\n\n\t -1 = "MINUTES" | -2 = "HOURS" | -3 = "DAYS" | -4 = "WEEKS" | -5 = "MONTHS" | -6 = "YEARS"\n')
			#if config_was_changed:
			cconfig['time'] = new_value[0]
			cconfig['time_type'] = new_value[1]
		elif choice == '4':
			new_value, config_was_changed = change_cataloguer('frequency', cconfig['frequency'], 'This is the frequency of candles you\'ll get.\n The value must be in seconds and must be equal to the candlen\'s IQ Option frequencies.')
			#if config_was_changed:
			cconfig['frequency'] = new_value
		
		#if config_was_changed:
		path = './data/cataloguer_config.txt'
		file = open(path, 'wb')
		pickle.dump(cconfig, file)
		file.close()
		config_was_changed = False

def change_cataloguer(command, value, description):
	error = ''
	new_value = value
	config_was_changed = False
	while True:
		print_top_menu_info('CATALOGUER: set ' + command)
		print(description)
		options_array = [
			['ANY', str(command) + ': ' + str(new_value)]
		]
		choice, error = create_options_menu(error, options_array, has_zero=False, type_reminder='Type what value you want it to be')
		if choice == '\'':
			break
		else:
			choice = int(choice)
			if choice == 0:
				error = 'Value can\'t be "0".'
			elif command == 'time':
				if choice < 0 and choice >= -6:
					new_value[1] = ['YEARS', 'MONTHS', 'WEEKS', 'DAYS', 'HOURS', 'MINUTES'][choice]
				elif choice < -6:
					error = 'Choice was lower than the options, must go from -1 to -6 to change the time type, but was ' + str(choice) + ' instead.'
				else:
					new_value[0] = int(choice)
				if new_value[1] == 'YEARS' and new_value[0] >= 2:
					error = ('WARNING: The settings in YEARS may be too heavy on processing and space needed, besides it may not have the history at IQ Option to catalogue everything until the end.\n' +
						'\tIT\'S NOT RECOMENDED TO HAVE "TIME" AT HIGH VALUES WHEN "TIME_TYPE" IS IN YEARS.')
			else:
				if choice < 0:
					error = 'The value can\'t be negative'
				else:
					new_value = int(choice)
	
	if new_value != value:
		config_was_changed = True

	return new_value, config_was_changed

# ----------------------------------------------------------------------------------------------------------------------------- #
		### PROGRAM ###

cataloguer = []
c_total_entries = 0

def new_catalogue(p):
	global cataloguer
	catalogue = {
		'done_entries': 0,
		'par': p,
	}
	cataloguer.append(catalogue)

def start_cataloguer(total_entries, timeframe, tipo_par, escopo):
	global cataloguer, c_total_entries
	par_all = API.get_all_open_time(type_to_get=tipo_par.lower())
	cataloguer_begin = int(str(time.time())[:10])
	escopo = time_converter(time.time())[:10] + escopo
	check_dir('./data/saved_entries/' + tipo_par)
	check_dir('./data/saved_entries/' + tipo_par + '/' + escopo)
	save_file('./data/unfinished_dirs.txt', ['./data/saved_entries/' + tipo_par + '/' + escopo])
	total_timer = int(perf_counter())
	
	for p in par_all[tipo_par.lower()]:
		if '-OTC' in p:
			pass
		else:
			new_catalogue(p)

	if __name__ == "__main__":
		cataloguer_progress = Array('i', 4)		#[Current, Total, Time, focus]
		cataloguer_progress[0] = 0
		cataloguer_progress[1] = total_entries
		cataloguer_progress[2] = cataloguer_begin
		cataloguer_progress[3] = -1

	processes = []
	id = 0
	for par in par_all[tipo_par.lower()]:
		for cat in range(len(cataloguer)):
			if cataloguer[cat]['par'] == par:
				index = cat
				break
		
		if '-OTC' not in par:
			p = Process(target=catalogue_par, args=(timeframe, tipo_par, escopo, par, id, cataloguer_progress, current_account))
			processes.append(p)
			id += 1
	
	use_cap = True		#ADM
	cap = math.ceil(len(processes)/2) #OLD: multiprocessing.cpu_count()

	if use_cap: 
		x = 0
		while x < len(processes):
			i = min(cap, len(processes)-x)
			for p in range(i):
				processes[p + x].start()
			for p in range(i):
				processes[p + x].join()
			x += i
	else:
		for p in processes:
			p.start()
		for p in processes:
			p.join()

	save_file('./data/unfinished_dirs.txt', [])
	cataloguer_screen(escopo, cataloguer_progress)
	print_separator()
	print('Catalogation done in ' + time_to_str(round(int(perf_counter()) - total_timer, 0)) + ', type any key to continue:', end=' ')
	confirm = input()
	c_total_entries = 0

def catalogue_par(timeframe, tipo_par, escopo, par, id, cataloguer_progress, current_account):
	success, info = decrypt_login(current_account)
	if success:
		connect = connect_iqoption(info[0], info[1], False)
		if connect == False:
			print('error connecting to IQ option')
			exit()
	else:
		print('error reaching for account in data')
		exit()

	datas_fechadas = []
	time_ = int(cataloguer_progress[2])
	day = datetime.fromtimestamp(time_).strftime('%Y-%m-%d')
	
	timer = int(perf_counter())
	entries = cataloguer_progress[1]
	f = open('./data/saved_entries/'+ tipo_par +'/'+ escopo +'/'+ str(timeframe) +'_'+ par +'_'+ day +'_'+ str(time_) +'.entries', 'wb')
	
	first_entry = True
	
	data = []
	show_delay = 0
	
	entries_gap = 1000
	while entries > 0:
		if cataloguer_progress[3] == -1:
			cataloguer_progress[3] = id

		e = min(entries, entries_gap)
		
		velas = API.get_candles(par, timeframe, e, time_)
		velas.reverse()
		
		for v in velas:
			data.append(v)
			first_entry = False
			vday = datetime.fromtimestamp(v['from']).strftime('%Y-%m-%d')
			if vday != day:
				day = vday
				pickle.dump(data, f)
				data = []
				f.close()
				f = open('./data/saved_entries/'+ tipo_par +'/'+ escopo +'/'+ str(timeframe) +'_'+ par +'_'+ day +'_'+ str(time_) +'.entries', 'wb')
				first_entry = True
		time_ = velas[-1]['from'] - 1
		entries -= len(velas)
		cataloguer_progress[0] += len(velas)

		if cataloguer_progress[3] == id:
			if show_delay <= 0:
				cataloguer_screen(escopo, cataloguer_progress)
				show_delay = (cataloguer_progress[1])/1000
			else:
				show_delay -= len(velas)

	if cataloguer_progress[3] == id:
		cataloguer_progress[3] = -1
		cataloguer_screen(escopo, cataloguer_progress)
	pickle.dump(data, f)
	data = []
	f.close()

def cataloguer_screen(escopo, cataloguer_progress):
	real_total = cataloguer_progress[1] * 23
	timer = int(str(time.time())[:10]) - cataloguer_progress[2]
	speed = round( cataloguer_progress[0] / max(timer,1) ,4)
	eta = math.floor( (real_total - cataloguer_progress[0]) / max(speed,1) )
	prct = round(cataloguer_progress[0] * 100 / real_total,1)

	os.system('cls')
	print(center_text('CATALOGING: ' + escopo))
	print_separator(2)
	print(center_text(''.join(['TOTAL: ',str(cataloguer_progress[0]),' of ',str(real_total),'  (',str(prct),'%) - ',time_to_str(timer)])))
	print()
	print(center_text(' '.join(['Speed:', str(math.floor(speed)), 'entries/s     -     ETA:', time_to_str(eta)])))


# █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ #

# ▓▓▓▓▓ # #   ███████╗██╗███╗   ███╗██╗   ██╗██╗      █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# ▓▓    # #   ██╔════╝██║████╗ ████║██║   ██║██║     ██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# ▓▓▓▓▓ # # # ███████╗██║██╔████╔██║██║   ██║██║     ███████║   ██║   ██║██║   ██║██╔██╗ ██║
# ▓▓ ▓▓ # #   ╚════██║██║██║╚██╔╝██║██║   ██║██║     ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# ▓▓▓▓▓ # # # ███████║██║██║ ╚═╝ ██║╚██████╔╝███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# # # # # #   ╚══════╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
# ----------------------------------------------------------------------------------------------------------------------------- #
		### MENU ###

def save_simulator_configuration():
	path = './data/simulator_configuration.txt'
	file = open(path, 'wb')
	pickle.dump(simulator_config, file)
	file.close()

def load_simulator_configuration():
	global simulator_config
	path = './data/simulator_configuration.txt'
	if os.path.isfile(path):
		config_file = open(path, 'rb')
		simulator_config = pickle.load(config_file)
		config_file.close()
	else:
		save_bot_configuration()

	file_path = './data/simulator/multiconfigs/configurations/' + simulator_config['mconfiguration'] + '.ini'
	if check_dir(file_path, 'none') == False:
		standard_path = './data/simulator/multiconfigs/configurations/Standard MConfig.ini'
		if check_dir(standard_path, 'none'):
			mconfig = load_parser(standard_path, type='list')
			simulator_config['mconfiguration'] = 'Standard MConfig'
			save_simulator_configuration()
		else:
			create_default_mconfiguration()
	mconfig = load_parser(file_path, type='list')
	simulator_config['status'] = mconfig['status'][0]
	simulator['config_progress'][1] = count_multiconfigs(mconfig)

def simulator_menu():
	global simulator_config
	reset_simulator()
	load_simulator_configuration()

	path = './data/simulator/multiconfigs/configurations'
	if len(list_files(path)) <= 0:
		create_default_mconfiguration()
	error = ''

	while True:
		if simulator_config['mode'] == 'multi-configs':
			file_path = './data/simulator/multiconfigs/configurations/' + simulator_config['mconfiguration'] + '.ini'
			mconfig = load_parser(file_path, type='list')
			simulator_config['status'] = mconfig['status'][0]
		else:
			if check_dir('./data/simulator/stats/' + simulator_config['catalogue'] + '/' + config['id'] + '.' + simulator_config['mode'], 'none'):
				simulator_config['status'] = 'DONE'
			else:
				simulator_config['status'] = 'READY'

		print_top_menu_info('SIMULATOR')
		print('The simulator uses the Cataloguer\'s saved entries to simulate a Configuration in a long term with speed, ' +
			'it is extremely faster than testing in real-time but it is slightly imprecise comparing to a real-life situation, ' +
			'which has a minor lag delay.\n\t To change the configuration used: go back to the menu and go into "Configurations".')
		
		options_array = [
			[1, 'Mode: ' + simulator_config['mode']],
			[2, 'Payout: ' + str(simulator_config['rend'])],
			[3, 'Processor Cores: ' + str(simulator_config['cores'])],
			[4, 'Catalogue: ' + simulator_config['catalogue']],
			['','']
		]
		
		if simulator_config['mode'] == 'multi-configs':
			options_array.append([5,'Multi-configuration: ' + simulator_config['mconfiguration']])
			options_array.append(['','Multi-configs Status: ' + simulator_config['status']])
			options_array.append(['','Total configs: ' + str(simulator['config_progress'][1])])
		else:
			options_array.append(['','single-config Status: ' + simulator_config['status']])
		
		choice, error = create_options_menu(error, options_array, back_text='Go back to menu', zero_text='Start simulator')
		if choice == '\'':
			break
		elif choice == '0':
			#Confirm delete previous simulation if multi-configs is active
			if simulator_config['catalogue'] == 'none':
				error = 'Please select a catalogue to simulate on. If you don\'t have any, make a catalogue in cataloguer at the menu.'
			else:
				to_simulator()
				break
		elif choice == '1':
			if simulator_config['mode'] == 'multi-configs':
				simulator_config['mode'] = 'single-config'
			else:
				simulator_config['mode'] = 'multi-configs'
			save_simulator_configuration()
		elif choice == '2':
			new_value = int(input('Type the new payout: '))
			if new_value != simulator_config['rend']:
				simulator_config['rend'] = new_value
				save_simulator_configuration()
		elif choice == '3':
			c = input('How many cores of your processor do you want to use? ')
			c = int(c)
			if c != simulator_config['cores']:
				simulator_config['cores'] = c
				save_simulator_configuration()
		elif choice == '4':
			new_catalogue = open_catalogue_list()
			if new_catalogue != simulator_config['catalogue']:
				simulator_config['catalogue'] = new_catalogue
				save_simulator_configuration()
		elif choice == '5' and simulator_config['mode'] == 'multi-configs':
			open_mconfiguration_menu()

def open_catalogue_list():
	error = ''
	path = './data/saved_entries/TURBO'
	new_catalogue = simulator_config['catalogue']
	
	while True:
		options_array = []
		for root, dirs, files in os.walk(path):
			id = 1
			for dir in dirs:
				options_array.append([id, dir])
				id += 1
		
		if len(options_array) <= 0:
			options_array.append(['', '* There\'s no catalogues in here, please create one in the cataloguer at menu *'])
		
		print_top_menu_info('SIMULATOR CATALOGUE LIST', False)
		choice, error = create_options_menu(error, options_array, has_zero=False)
		if choice == '\'':
			return new_catalogue
		elif error == '':
			return options_array[int(choice)-1][1]

#MULTI-CONFIGURATION SIMULATION
def open_mconfiguration_menu():
	global simulator_config, simulator
	error = ''
	while True:
		print_top_menu_info('SIMULATOR > Multi-simulation configuration list')
		options_array = []
		id = 1
		path = './data/simulator/multiconfigs/configurations'
		for file in list_files(path):
			array = file.split('.')
			options_array.append([id, array[0]])
			id += 1

		choice, error = create_options_menu(error, options_array, zero_text='New mconfiguration')
		if choice == '\'':
			break
		elif choice == '0':
			success = new_mconfiguration()
			if success:
				break
		elif int(choice) <= id:
			if simulator_config['mconfiguration'] != options_array[int(choice)-1][1]:
				simulator_config['mconfiguration'] = options_array[int(choice)-1][1]
				simulator['config_progress'][1] = count_multiconfigs(load_parser('./data/simulator/multiconfigs/configurations/' + simulator_config['mconfiguration'] + '.ini', type='list'))
				save_simulator_configuration()
				break
			else:
				error = 'Choosen multi-configuration already selected: ' + options_array[int(choice)-1][1]

def new_mconfiguration():
	global simulator_config
	error = ''
	banned_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
	path = './data/simulator/multiconfigs/configurations/'
	while True:
		name = input('What name do you want give to the configuration?\n\t')
		if name == '':
			error = 'Please do right a name, no-input is not allowed.'
		elif any(ele in name for ele in banned_chars): 
			error = 'Attempt: ' + name + '\nSorry, but it\'s not possible to use special character like: "\\", "/", ":", "*", "?", """, "<", ">", or "|"'
		elif name == '\'':
			return False
		elif name == '\'s':
			exit()
		elif (name + '.ini') in list_files(path):
			error = 'Sorry, but ' + name + ' already exists.'
		else:
			file_path = path + name + '.ini'
			copy_mconfigs = load_parser(path + simulator_config['mconfiguration'] + '.ini', type='list')
			copy_mconfigs['status'] = ['TO-BUILD']
			save_parser(file_path, copy_mconfigs, 'MULTI_SIMULATION_CONFIGURATION')

			print('\nMake your changes, save the .ini file and close it to continue.')
			#webbrowser.open(file_path)
			os.system('"data/simulator/multiconfigs/configurations/' + name + '.ini"')			#WINDOWS ONLY
			#os.startfile('"/data/simulator/multiconfigs/configurations/' + name + '.ini"')
			#subprocess.run(['open', file_path], check=True)

			simulator_config['mconfiguration'] = name
			simulator_config['status'] = 'TO-BUILD'
			save_simulator_configuration()
			simulator['config_progress'][1] = count_multiconfigs(load_parser('./data/simulator/multiconfigs/configurations/' + simulator_config['mconfiguration'] + '.ini', type='list'))
			return True

def create_default_mconfiguration():
	path = './data/simulator/multiconfigs/configurations/Standard MConfig.ini'
	info = {'status': ['TO-BUILD'],
			'sma_period': [20,50,125],
			'bband_threshold': [-0.08,0.00,0.08],
			'bbands_period': [20,50,125],
			'bbands_desvio': [1.0,2.0,3.0],
			'power_for_middle': [0,1,2],
			'watch_sensor_id': [0,1,2,3,4],
			'open_bet_seconds': [40,60],
			'when_hit_top': ['down', 'up', 'none'],
			'when_hit_bot': ['down', 'up', 'none']}
	save_parser(path, info, 'MULTI_SIMULATION_CONFIGURATION')

# ----------------------------------------------------------------------------------------------------------------------------- #
		### PROGRAM ###

def to_simulator():
	global simulator, config, pars, multi_progress
	reset_simulator()
	reset_bot_stats(False)
	multi_progress = Array('i', 6)
	configs_path = './data/simulator/multiconfigs/' + simulator_config['mconfiguration'] + '/'
	mconfig_path = './data/simulator/multiconfigs/configurations/' + simulator_config['mconfiguration'] + '.ini'

	choose_to_back = False

	path = './data/simulator/rawtest/' + simulator_config['catalogue']
	check_dir(path)

	#check simulator config status
	if simulator_config['status'] == 'DONE':
		error = ''
		while True:
			os.system('cls')
			print('\tIt seems like the simulation was already done once, or had the attempt to do so, ' +
				'it\'s best to delete the previous simulation data so the program can work properly.')
			print_separator()
			print(error)
			error = ''
			stats_path = './data/simulator/stats/'+ simulator_config['mode'] +'/'+ simulator_config['mconfiguration'] +'/'+ simulator_config['catalogue'] +'.'+ simulator_config['mode']
			choice = input('\nWhere do you want to reset this configuration?' +
					'\n\t B - "TO-BUILD", it will rebuilt the configs, deleting previous ones' +
					'\n\t R - "READY", it will resimulate with existing configs\n\t \' - Cancel, go back to simulation' +
					'\n\n\t O - open the result of the done simulation.' + 
					'\n')
			if choice == '\'':
				choose_to_back = True
				break
			elif choice == '\'s':
				exit()
			elif choice.lower() == 'b':
				mconfig = load_parser(mconfig_path, 'list')
				simulator_config['status'] = 'TO-BUILD'
				mconfig['status'] = ['TO-BUILD']
				save_parser(mconfig_path, mconfig, 'MULTI_SIMULATION_CONFIGURATION')
				os.remove(stats_path)
				delete_all_files_in_dir('./data/simulator/'+ simulator_config['mode'] +'/'+ simulator_config['mconfiguration'])
				break
			elif choice.lower() == 'r':
				mconfig = load_parser(mconfig_path, 'list')
				simulator_config['status'] = 'READY'
				mconfig['status'] = ['READY']
				save_parser(mconfig_path, mconfig, 'MULTI_SIMULATION_CONFIGURATION')
				os.remove(stats_path)
				break
			elif choice.lower() == 'o':
				if simulator_config['mode'] == 'multi-configs':
					title = simulator_config['mconfiguration']
				else:
					title = friendly_file_name(config['name'])
				simulator['configs_results'] = load_file(''.join(['data/simulator/stats/', simulator_config['mode'], '/', title, '/', simulator_config['catalogue'], '.', simulator_config['mode']]))
				show_simulator_results()
			else:
				error = '"' + choice + '" is not an option, choose B, R, or \'.'
	if choose_to_back:
		return

	#preparing for simulation
	reset_bot_stats(False)
	check_dir(''.join(['data/simulator/stats/', simulator_config['mode']]))
	simulator['total_timer'] = int(perf_counter())
	multi_progress[2] = int(time.time())

	#multi-configs
	if simulator_config['mode'] == 'multi-configs':
		check_dir(''.join(['data/simulator/stats/', simulator_config['mode'], '/', simulator_config['mconfiguration']]))
		stats_path = ''.join(['data/simulator/stats/', simulator_config['mode'], '/', simulator_config['mconfiguration'], '/', simulator_config['catalogue'], '.', simulator_config['mode']])

		if simulator_config['status'] == 'TO-BUILD':
			get_configs_simulator()
		file_list = list_files(configs_path)
		simulator['config_progress'][1] = len(file_list)
		
		if check_dir(stats_path, 'none'):
			simulator['configs_results'] = load_file(stats_path)

		result_keys = simulator['configs_results'].keys()
		checking_completed = False
		settup_simulator()
		for file in file_list:
			config_id = file[:-4]
			if checking_completed or config_id not in result_keys:
				config = load_file(configs_path + file)
				start_simulator()
				reset_bot_stats(False)
				save_configuration_simulator()
				save_file(stats_path, simulator['configs_results'])
				checking_completed == True
			else:
				multi_progress[5] += 1
				simulator['config_progress'][0] += 1
	
	#single-config
	else:
		simulator['config_progress'][1] = 1
		settup_simulator()
		check_dir(''.join(['data/simulator/stats/', simulator_config['mode'], '/', simulator['file_title']]))
		stats_path = ''.join(['data/simulator/stats/', simulator_config['mode'], '/', simulator['file_title'], '/', simulator_config['catalogue'], '.', simulator_config['mode']])
		
		start_simulator()
		save_configuration()

	#wrap-up
	print('Sorting config_results, it may take a while')
	sort_config_results()
	save_file(stats_path, simulator['configs_results'])

	simulator_config['status'] == 'DONE'
	if simulator_config['mode'] == 'multi-configs':
		mconfig = load_parser(mconfig_path, 'list')
		mconfig['status'] = ['DONE']
		save_parser(mconfig_path, mconfig, 'MULTI_SIMULATION_CONFIGURATION')

	input('FINISHED: Do you wish to continue?')
	show_simulator_results()

def settup_simulator():
	global simulator, multi_progress, pars

	simulator['max_period'] = max(config['sma_period'], config['bbands_period'])-1
	simulator['pars_list'].clear()
	simulator_pars_list = []
	pars.clear()

	#Create dictionary of par in simulator
	id = 0
	for root, dirs, files in os.walk('./data/saved_entries/TURBO/' + simulator_config['catalogue']):
		for file in files:
			name = file[2:8]
			if name not in simulator['multi_simulation']:
				simulator['file_progress'][1] += 1
				simulator['multi_simulation'][name] = {}
				simulator['multi_simulation'][name]['name'] = name
				simulator['multi_simulation'][name]['files'] = []
				simulator_pars_list.append(name)
				simulator['multi_simulation'][name]['par'] = simulator_pars_list.index(name)
				simulator['bet_list'][name] = []
				simulator['multi_simulation'][name]['in_bet'] = False
				simulator['multi_simulation'][name]['id'] = id
				id += 1
			simulator['multi_simulation'][name]['files'].append('./data/saved_entries/TURBO/' + simulator_config['catalogue'] + '/' + file)
	
	betholder_path = './data/simulator/rawtest/'+ simulator_config['catalogue'] + '/'
	check_dir(betholder_path)
	simulator['file_title'] = friendly_file_name(config['name'])

	#Prepare multiprocessing vars in shared memory
	simulator['entries_progress'][1] = -simulator['max_period'] -1
	for file in simulator['multi_simulation'][list(simulator['multi_simulation'].keys())[0]]['files']:
		with open(file, 'rb') as f:
			entries = pickle.load(f)
			simulator['entries_progress'][1] += len(entries)

	#multi_progress[1] = simulator['entries_progress'][1] * len(simulator['multi_simulation']) * len(simulator['multi_simulation'][list(simulator['multi_simulation'].keys())[0]]['files']) * simulator['config_progress'][1]
	multi_progress[1] = simulator['entries_progress'][1] * simulator['file_progress'][1] * simulator['config_progress'][1]
	multi_progress[3] = -1

# ----------------------------------------------------------------------------------------------------------------------------- #
		### MULTI-CONFIGURATIONS ###

def count_multiconfigs(mconfig):
	total = 0
	print(mconfig)
	for sma_period in mconfig['sma_period']:
		for bband_threshold in mconfig['bband_threshold']:
			for bbands_periodo in mconfig['bbands_period']:
				for bbands_desvio in mconfig['bbands_desvio']:
					for poder_para_meio in mconfig['power_for_middle']:
						for watch_sensor_id in mconfig['watch_sensor_id']:
							for open_bet_seconds in mconfig['open_bet_seconds']:
								for when_hit_top in mconfig['when_hit_top']:
									for when_hit_bot in mconfig['when_hit_bot']:
										if when_hit_top == 'none' and when_hit_bot == 'none':
											continue
										total += 1
	return total

def get_configs_simulator():
	global simulator, config, simulator_config
	reset_config()
	
	total_timer = int(perf_counter())
	path = './data/simulator/multiconfigs'
	mconfig_path = path + '/configurations/' + simulator_config['mconfiguration'] + '.ini'
	configs_path = path + '/' + simulator_config['mconfiguration'] + '/'
	mconfig = load_parser(mconfig_path, 'list')

	config['use_mood'] = False
	id = 0
	total_configs = count_multiconfigs(mconfig)
	show_delay = 0

	check_dir(configs_path)
	for sma_period in mconfig['sma_period']:
		for bband_threshold in mconfig['bband_threshold']:
			for bbands_periodo in mconfig['bbands_period']:
				for bbands_desvio in mconfig['bbands_desvio']:
					for poder_para_meio in mconfig['power_for_middle']:
						for watch_sensor_id in mconfig['watch_sensor_id']:
							for open_bet_seconds in mconfig['open_bet_seconds']:
								for when_hit_top in mconfig['when_hit_top']:
									for when_hit_bot in mconfig['when_hit_bot']:
										if when_hit_top == 'none' and when_hit_bot == 'none':
											continue
										config['sma_period'] = sma_period
										config['bband_threshold'] = bband_threshold
										config['bbands_period'] = bbands_periodo
										config['bbands_desvio'] = bbands_desvio
										config['power_for_middle'] = poder_para_meio
										config['watch_sensor_id'] = watch_sensor_id
										config['open_bet_seconds'] = open_bet_seconds
										config['when_hit_top'] = when_hit_top
										config['when_hit_bot'] = when_hit_bot
										config['name'] = ' '.join([simulator_config['mconfiguration'] ,'configuration', str(id)])
										id += 1
										this_path = ''.join([configs_path, calculate_config_id(), '.txt'])
										if check_dir(this_path, 'none') == False:
											save_file(this_path, config)
										if show_delay <= 0:
											timer = int(perf_counter()) - total_timer
											show_get_config_progress(id, total_configs, timer)
											show_delay = math.floor(total_configs/100)
										else:
											show_delay -= 1
	simulator_config['status'] = 'READY'
	mconfig['status'] = ['READY']
	save_parser(mconfig_path, mconfig, 'MULTI_SIMULATION_CONFIGURATION')
	save_simulator_configuration()

def show_get_config_progress(done, total, timer):
	speed = round(done/max(timer,1),4)

	os.system('cls')
	print(center_text('GENERATING CONFIGURATIONS:'))
	print_separator(2)
	print(str(done) + ' of ' + str(total) + ' configs   (' + str(round((done/total)*100,1)) + '%)  -  ' + time_to_str(timer))
	print_separator()
	print('\n')
	print(center_text('Speed: ' + str(math.floor(speed)) + ' configs/s     -     ETA: ' + time_to_str(math.floor(total/max(speed,1))-timer)))

def save_configuration_simulator():
	path = './data/simulator/multiconfigs/' + simulator_config['mconfiguration'] + '/' + config['id'] + '.txt'
	file = open(path, 'wb')
	pickle.dump(config, file)
	file.close()

# ----------------------------------------------------------------------------------------------------------------------------- #
		### SIMULATION ###

def start_simulator():
	global simulator, bot_stats, pars, config_id, config, multi_progress, multi_result
	
	#Preload
	set_globals_onda()
	reset_bot_stats(real=False)

	for command in ['winrate', 'total_wins', 'total_bets']:
		config[command][2] = 0
		config[command][0] = config[command][1]
	config['total_payout'][1] = 0

	multi_result = Array('i', (1 + len(simulator['multi_simulation']))*5)

	#Multiprocessing
	if __name__ == "__main__":
		processes = []
		core_limit = simulator_config['cores']		#OPTIMIZE
		use_cpu_cap = True		#ADM
		cpu_usage = [0,core_limit,0.0]
		progresses = {}

		for key in ['config_progress', 'file_progress', 'entries_progress']:
			progresses[key] = simulator[key]

		percentage = max(multi_progress[1]/(1000/core_limit), 11000*core_limit)
		for key in simulator['multi_simulation'].values():
			key['show_progress'] = percentage
			p = Process(target=simulate_multi, 
				args=(dict(key), simulator['file_title'], progresses, simulator_config, config, multi_progress, multi_result, cpu_usage))
			processes.append(p)
		
		x = 0
		process_power = 0
		
		cpu_prct = 0 #get_outer_cpu_usage()

		if use_cpu_cap:
			while len(processes) != x:
				#for i in range(core_limit-1):
				#	if cpu_prct/100 < (i+1)/core_limit:
				#		process_power = core_limit-(i+1)
				#		break
				cpu_usage[0] = min(cpu_usage[1], len(processes)-x)		#min(int(round(process_power,0)), len(processes)-x, process_power, cpu_usage[1])

				for i in range(cpu_usage[0]):
					processes[i + x].start()

				#cpu_prct = get_outer_cpu_usage()			#TEMP
				check_show_progress_simulator(multi_progress, multi_result, cpu_usage)

				for i in range(cpu_usage[0]):
					processes[i + x].join()
				x += cpu_usage[0]
				simulator['file_progress'][0] += int(cpu_usage[0])
				
				if cpu_usage[0] == 0:
					time.sleep(3)
		else:
			for p in processes:
				p.start()
			check_show_progress_simulator(multi_progress, multi_result, ['all', core_limit])
			for p in processes:
				p.join()
	simulator['config_progress'][0] += 1
	check_show_progress_simulator(multi_progress, multi_result, cpu_usage)
	simulator['file_progress'][0] = 0

	#Take results
	bot_stats['wdl'][0] = multi_result[0]
	bot_stats['wdl'][1] = multi_result[1]
	bot_stats['wdl'][2] = multi_result[2]
	bot_stats['total_bets'] = sum(bot_stats['wdl'])
	bot_stats['total_combo_history'][0] = multi_result[3]
	bot_stats['total_combo_history'][1] = multi_result[4]

	#Transform to config then save
	config['total_wins'][2] = bot_stats['wdl'][0]
	config['total_wins'][0] = config['total_wins'][1] + config['total_wins'][2]
	config['total_bets'][2] = bot_stats['wdl'][0] + bot_stats['wdl'][2]
	config['total_bets'][0] = config['total_bets'][1] + config['total_bets'][2]
	config['winrate'][0] = round(config['total_wins'][0] * 100 / max(config['total_bets'][0],1),2)
	config['winrate'][2] = round(config['total_wins'][2] * 100 / max(config['total_bets'][2],1),2)
	config['total_payout'][1] = float(bot_stats['wdl'][0] - bot_stats['wdl'][2])
	if simulator_config['mode'] == 'multi-configs':
		save_configuration_simulator()
	else:
		save_configuration()

	#Transform to stats
		#global
	wdl = list(bot_stats['wdl'])
	combo = list(bot_stats['total_combo_history'])
	if 0 > wdl[0] - wdl[1]:
		wdl.reverse()
		combo.reverse()

	if 'wdl' not in simulator['configs_results']:
		simulator['configs_results']['wdl'] = list(wdl)
		simulator['configs_results']['combo'] = list(combo)
	else:
		for i in range(len(simulator['configs_results']['wdl'])):
			simulator['configs_results']['wdl'][i] += wdl[i]
		for i in range(len(simulator['configs_results']['combo'])):
			if simulator['configs_results']['combo'][i] < combo[i]:
				simulator['configs_results']['combo'][i] = combo[i]

		#configs
	dict_to_add = {}
	dict_to_add['wdl'] = list(bot_stats['wdl'])
	dict_to_add['combo'] = list(bot_stats['total_combo_history'])
	
		#pars
	id = 0
	for simul in simulator['multi_simulation'].values():
		wdl = [0,0,0]
		combo = [0,0]
		position = (1 + id) *5

		wdl[0] = int(multi_result[position])
		wdl[1] = int(multi_result[position + 1])
		wdl[2] = int(multi_result[position + 2])
		combo[0] = int(multi_result[position + 3])
		combo[1] = int(multi_result[position + 4])

		dict_to_add[simul['name']] = {}
		dict_to_add[simul['name']]['wdl'] = wdl
		dict_to_add[simul['name']]['combo'] = combo
		id += 1
	simulator['configs_results'][config['id']] = dict_to_add

def get_outer_cpu_usage():
	p = psutil.Process(os.getpid())
	self_cpu = 0
	for o in p.parent().children(recursive=True): 
		try:
			self_cpu += o.cpu_percent(interval=0.1)
		except:
			pass
	return psutil.cpu_percent(interval=0.1) - self_cpu

def sort_config_results():
	global simulator

	new_dict = dict(simulator['configs_results'])
	final_dict = {}
	id_rank = []
	par_rank = []

	for id in simulator['configs_results'].keys():
		if id != 'wdl' and id != 'combo':
			value = (simulator['configs_results'][id]['wdl'][0]/max(simulator['configs_results'][id]['wdl'][2],1)) - 1
			for par in simulator['configs_results'][id].keys():
				if par != 'wdl' and par != 'combo':
					value_par = simulator['configs_results'][id][par]['wdl'][0]/max(simulator['configs_results'][id][par]['wdl'][2],1)
					if value < 0:
						value_par = -1*value_par
					par_rank.append([value_par ,par])
			value = abs(value)
			id_rank.append([value ,id])
			par_rank = sorted(par_rank)
			new_dict[id] = {}
			for p in par_rank:
				new_dict[id][p[1]] = simulator['configs_results'][id][p[1]]
			new_dict[id]['wdl'] = simulator['configs_results'][id]['wdl']
			new_dict[id]['combo'] = simulator['configs_results'][id]['combo']
			par_rank.clear()
	
	id_rank = sorted(id_rank)
	simulator['configs_results'] = {}
	for i in id_rank:
		simulator['configs_results'][i[1]] = new_dict[i[1]]
	simulator['configs_results']['wdl'] = new_dict['wdl']
	simulator['configs_results']['combo'] = new_dict['combo']

#CACHE CHECK AND CALCULATION (LOAD AND SAVE)
def get_valores_simulator(velas):
	valores = dict(global_valores)
	keys = [['open', 'open'], ['high', 'max'], ['volume', 'volume'], ['from', 'from']]
	for vela in velas:
		for key in keys:
			valores[key[0]] = np.append(valores['open'], vela[key[1]])
	for key in [['volume', 'volume'], ['from', 'from']]:
		valores[key[0]] = valores['open']
		valores[key[0]] = np.append(valores['open'], vela[key[1]])
	for key in ['low', 'close']:
		valores[key] = valores['high']
	return valores

def check_cache_simulator(files):
	max_period = max(config['sma_period'], config['bbands_period'])
	cache = {}

	get_opvalues = True
	get_values = True
	get_bbands = True
	get_tide = True
	get_sma = True

	path = 'data/simulator/cache/' + simulator_config['catalogue'] + '/' + pars[0]['name'] + '/PERIOD_' + str(max_period) + '/'
	opvalues_path = ''.join(['data/simulator/cache/', simulator_config['catalogue'], '/', pars[0]['name'], '/opvalues.list'])
	path_bbands = path +'bbands/'+ str(config['bbands_period']) +'_'+ str(config['bbands_desvio']) + '.bbands'
	path_tide = path + 'tide/' + str(config['sma_period']) + '_' + str(config['mov_sensors']) + '.tide'
	path_sma = path + 'sma/' + str(config['sma_period']) + '.sma'

	#Check
	path = 'data/simulator/cache'
	if check_dir(path):
		path = path + '/' + simulator_config['catalogue']
		if check_dir(path):
			path = path + '/' + pars[0]['name']
			if check_dir(path):
				get_opvalues = False
				path = path + '/PERIOD_' + str(max_period)
				if check_dir(path):
					path = path + '/'
					get_values = False

					#BBANDS
					if check_dir(path_bbands, 'none'):
						get_bbands = False

					#TIDE
					if check_dir(path_tide, 'none'):
						get_tide = False
					else:
						#SMA
						if check_dir(path_sma, 'none'):
							get_sma = False

	#Calculate
	path = 'data/simulator/cache'

	if get_opvalues:
		dirs = [
			''.join([path, '/', simulator_config['catalogue']]),
			''.join([path, '/', simulator_config['catalogue'], '/', pars[0]['name']]) ]
		for folder in dirs:
			check_dir(folder)
		cache_opvalues(files)

	if get_values:
		dirs = [
			''.join([path, '/', simulator_config['catalogue'], '/', pars[0]['name'], '/PERIOD_', str(max_period)]),
			''.join([path, '/', simulator_config['catalogue'], '/', pars[0]['name'], '/PERIOD_', str(max_period), '/bbands']),
			''.join([path, '/', simulator_config['catalogue'], '/', pars[0]['name'], '/PERIOD_', str(max_period), '/tide']),
			''.join([path, '/', simulator_config['catalogue'], '/', pars[0]['name'], '/PERIOD_', str(max_period), '/sma']),
			''.join([path, '/', simulator_config['catalogue'], '/', pars[0]['name'], '/PERIOD_', str(max_period), '/values'])
		]
		for folder in dirs:
			check_dir(folder)
		cache_values(files)

	path = 'data/simulator/cache/' + simulator_config['catalogue'] + '/' + pars[0]['name'] + '/PERIOD_' + str(max_period) + '/'
	if get_bbands:
		check_dir(path + 'bbands/')
		cache_bbands()

	if get_tide:
		if get_sma:
			check_dir(path + 'sma/')
			cache['sma'] = cache_sma()
		else:
			cache['sma'] = load_file(path_sma)
		check_dir(path + 'tide/')
		cache_tide(cache['sma'])

	cache['values'] = load_file(opvalues_path)
	cache['bbands'] = load_file(path_bbands)
	if get_tide == False:
		cache['sma'] = load_file(path_sma)
	cache['tide'] = load_file(path_tide)
	return cache

def cache_opvalues(files):
	max_period = max(config['sma_period'], config['bbands_period'])
	opvalues_path = ''.join(['data/simulator/cache/', simulator_config['catalogue'], '/', pars[0]['name'], '/opvalues.list'])
	optimized_values = []

	for file in files:
		entries_file = open(file, 'rb')
		entries = pickle.load(entries_file)
		entries_file.close()
		entries.reverse()

		for entry in entries:
			optimized_values.append({
					'close': [entry['close']], 
					'from': [entry['from']] })

	save_file(opvalues_path, optimized_values)
	return optimized_values

def cache_bbands():
	max_period = max(config['sma_period'], config['bbands_period'])
	path = ''.join(['data/simulator/cache/', simulator_config['catalogue'], '/', pars[0]['name'], '/PERIOD_', str(max_period), '/'])
	bbands_cache = []
	
	values_path = ''.join([path, 'values/'])
	for file in sorted(list_files(values_path), key=len):
		values = load_file(values_path + file)
		for valores in values:
			b_up, b_mid, b_low = BBANDS(valores, config['bbands_period'], config['bbands_desvio'], config['bbands_desvio'], 0)

			price = float(valores['close'][-1])-float(b_low[-1])
			high = float(b_up[-1])-float(b_low[-1])
			if high == 0:
				bbands = 0.54321		#Valor de erro
			else:
				bbands = round(price/high, 6)
			bbands_cache.append(locals()['bbands'])

	bbands_path = path + 'bbands/' + str(config['bbands_period']) +'_'+ str(config['bbands_desvio']) + '.bbands'
	save_file(bbands_path, bbands_cache)
	return bbands_cache

def cache_sma():
	max_period = max(config['sma_period'], config['bbands_period'])
	path = ''.join(['data/simulator/cache/', simulator_config['catalogue'], '/', pars[0]['name'], '/PERIOD_', str(max_period), '/'])
	sma = []

	values_path = ''.join([path, 'values/'])
	for file in sorted(list_files(values_path), key=len):
		values = load_file(values_path + file)
		for valores in values:
			sma.append(round(float(SMA(valores, config['sma_period'], price='close')[-1]), 6))
		
	sma_path = path + 'sma/' + str(config['sma_period']) + '.sma'
	save_file(sma_path, sma)
	return sma

def cache_tide(sma):
	tide = list(global_tide)
	total_tide = list(global_tide)
	mar = list(global_mar)
	cache_tide = []
	cache_tide.append(locals()['tide'])
	
	for s in range(len(sma)-1):
		if sma[s+1] > sma[s]:
			direction = 1		#'up'
		elif sma[s+1] < sma[s]:
			direction = -1	#'down'
		else:
			direction = 0		#'middle'

		for mov in range(len(config['mov_sensors'])):
			power_pop = mar[-config['mov_sensors'][mov]]
			total_tide[mov] = total_tide[mov] + (direction - power_pop)
			tide[mov] = max(min(total_tide[mov]*3/config['mov_sensors'][mov],3),-3)
		mar.pop(0)
		mar.append(direction)
		cache_tide.append(locals()['tide'])

	max_period = max(config['sma_period'], config['bbands_period'])
	path = ''.join(['data/simulator/cache/', simulator_config['catalogue'], '/', pars[0]['name'], '/PERIOD_', str(max_period), '/'])
	tide_path = path + 'tide/' + str(config['sma_period']) + '_' + str(config['mov_sensors']) + '.tide'
	save_file(tide_path, cache_tide)
	return cache_tide

def cache_values(files):
	max_period = max(config['sma_period'], config['bbands_period'])
	path = ''.join(['data/simulator/cache/', simulator_config['catalogue'], '/', pars[0]['name'], '/PERIOD_', str(max_period), '/values/'])
	values = []
	first_bet_entry = True
	velas = []
	id = 0
	entries_count = 0
	separator_amount = (6354595/(max_period+9))-1 #86164   x 50
	print('Calculating Values\' cache, do not exit.')

	for file in files:
		entries_file = open(file, 'rb')
		entries = pickle.load(entries_file)
		entries_file.close()
		entries.reverse()
		
		entries_len = len(entries)
		
		if first_bet_entry:
			entries_len -= max_period
			for e in range(max_period):
				velas.append(entries[e])
			velas.insert(0, {'open':0, 'max':0, 'min':0, 'close':0, 'volume':0, 'from':0})
			valores = get_valores_simulator(velas)
			first_bet_entry = False
			modifier = max_period
		else:
			modifier = 0

		for entry in range(entries_len):
			#prepare values
			for key in [['open', 'open'], ['from', 'from']]:			#or "global_keys" if all
				valores[key[0]] = np.delete(valores[key[0]], 0)
				valores[key[0]] = np.append(valores['open'], entries[entry+modifier][key[1]])

			for key in [['high', 'max'], ['volume', 'volume']]:
				valores[key[0]] = valores['open']
				valores[key[0]] = np.append(valores['open'], entries[entry+modifier][key[1]])

			for key in ['low', 'close']:
				valores[key] = valores['high']
			values.append(dict(valores))
			
			entries_count += 1
			if entries_count > separator_amount:		#one day
				values_path = path + str(id) + '.values'
				save_file(values_path, values)
				values = []
				entries_count = 0
				id += 1

	if len(values) > 0:
		values_path = path + str(id) + '.values'
		save_file(values_path, values)


#SIMULATION USING MULTIPROCESSING
def simulate_multi(name_dict, file_title, progresses, simulator_config_taken, config_taken, progress_taken, result_taken, cpu_usage):
	global simulator, simulator_config, bot_stats, pars, config_id, config, multi_progress, multi_result

	#Preload
	par = 0
	name = name_dict['name']
	done_entries = 0

	#Setup
	progress = progress_taken
	result = result_taken
	simulator_config = simulator_config_taken
	config = config_taken
	set_globals_onda()
	reset_bot_stats(real=False)
	pars.append(new_par(['100', 'OK', name]))

	simulation = {
			'in_bet': False,
			'bet_list': [],
			}
	simulator = progresses

	#Cache
	cache = check_cache_simulator(name_dict['files'])

	#Start to simulate from cache:
	max_period = max(config['sma_period'], config['bbands_period'])
	for i in range(len(cache['bbands'])):
		runbot_simulator(cache['bbands'][i], cache['sma'][i], cache['tide'][i], cache['values'][i+max_period])

		if simulation['in_bet']:
			if pars[par]['bet'] <= 0:
				simulation['bet_list'][-1]['result'] = pars[par]['bet_last_result']
				simulation['bet_list'][-1]['end_value'] = pars[par]['valor']
				simulation['in_bet'] = False
		else:
			if pars[par]['bet'] > 0:
				simulation['in_bet'] = True
				simulation['bet_list'].append({
						'time': bot_stats['hour'],
						'seconds': pars[par]['last_second'], 
						'bbands': cache['bbands'][i], 
						'tide': cache['tide'][i], 
						'bet': pars[par]['bet'],
						'bet_id': pars[par]['bet_id'],
						'bet_type': pars[par]['bet_type'],
						'end_value': 0,
						'result': ''})

	#Finalize by setting up shared memory variables and saving keep_bet_file
	for x in range(3):
		result[x] += bot_stats['wdl'][x]
	
	for x in range(2):
		if bot_stats['total_combo_history'][x] > result[x+3]:
			result[x+3] = bot_stats['total_combo_history'][x]

	keys = [pars[par]['wdl'][0], pars[par]['wdl'][1], pars[par]['wdl'][2], pars[par]['combo_history'][0], pars[par]['combo_history'][1]]
	for x in range(5):
		result[ ( (1 + name_dict['id']) *5 ) + x] = int(keys[x])

	path = './data/simulator/rawtest/'+ simulator_config['catalogue'] + '/' + config['id'] + '/'
	check_dir(path)
	betholder_path = path + pars[par]['name'] +'.betholder'
	with open(betholder_path, 'wb') as keep_bet_file:
		pickle.dump(simulation['bet_list'], keep_bet_file)

def check_show_progress_simulator(progress, result, cpu_usage):
	global simulator

	total_progress = simulator['entries_progress'][1] * simulator['file_progress'][1] * simulator['config_progress'][1]
	current_progress = (simulator['entries_progress'][0] + simulator['entries_progress'][1] * simulator['file_progress'][0] +
			simulator['entries_progress'][1] * simulator['file_progress'][1] * simulator['config_progress'][0])
	old_progress = simulator['entries_progress'][1] * simulator['file_progress'][1] * progress[5]

	timer = int(time.time()) - progress[2]
	speed = (current_progress-old_progress)/max(timer, 1)
	eta = math.floor( (total_progress - current_progress) / max(speed,1) ) 	#OLD: eta = math.floor(progress[1]/max(speed,1))-timer
	bets = result[0] + result[1] + result[2]
	
	show_simulator_progress(timer, current_progress, total_progress, speed, bets, cpu_usage, eta)			#OPTIMIZE

def show_simulator_progress(timer, total_done_progress, total_progress, speed, bets, cpu_usage, eta):
	os.system('cls')
	print(center_text('SIMULATION IN PROGRESS:'))
	print_separator(2)
	print(center_text(''.join(['Total progress: ', str(total_done_progress), ' of ', str(total_progress), 
		'  (', str(round((total_done_progress/max(total_progress,1))*100,1)), '%)  -  ', time_to_str(timer)])))
	print_separator()
	print('\n')
	for p in [['Configs', 'config_progress'], ['Files', 'file_progress'], ['Entries', 'entries_progress']]:
		print(center_text(''.join([p[0], ': ', str(simulator[p[1]][0]), ' / ', str(simulator[p[1]][1]), 
			'   (', str(round((simulator[p[1]][0]/simulator[p[1]][1])*100,1)), '%)'])))
	print('\n')
	print_separator()
	print('\n')
	print(center_text(' '.join([ 'Speed:', str(math.floor(speed)), 'entries/s     -     ETA:', time_to_str(eta), 
		'     -     BETS: ', str(bets), '  \tCPU: ', str(cpu_usage[0]), '/', str(cpu_usage[1]), '  (', str(cpu_usage[2]),'% )' ])))

def runbot_simulator(bbands, sma, tide, valores):
	global bot_stats, pars
	par = 0
	
	#Update	
	pars[par]['sma'] = sma

	tempo = str(datetime.utcfromtimestamp(valores['from'][-1]).strftime('%Y-%m-%d %H:%M:%S'))
	bot_stats['hour'] = tempo
	pars[par]['last_second'] = int(tempo[-2:])
	bot_stats['minuto'] = int(tempo[-5:][:-3])
	pars[par]['valor'] = valores['close'][-1]
	pars[par]['last_bbands'] = bbands

	#seta
	watch = config['watch_sensor_id']
	if tide[watch] > config['power_for_middle']:
		pars[par]['arrow'] = 'up'
	elif tide[watch] < -config['power_for_middle']:
		pars[par]['arrow'] = 'down'
	else:
		pars[par]['arrow'] = 'middle'

	#bet
	check_bet(par, False)

# ----------------------------------------------------------------------------------------------------------------------------- #
		### SHOW SCREEN ###

def show_simulator_results():
	if simulator_config['mode'] == 'multi-configs':
		simulator_results_screen(simulator['configs_results'], simulator_config['catalogue'], simulator_config['mconfiguration'])
	else:
		for key in simulator['configs_results'].keys():
			if key != 'wdl' and key != 'combo':
				simulator_results_screen(simulator['configs_results'][key], simulator_config['catalogue'] + ' → ' + key[:12], config['id'])
				break

	reset_simulator()
	load_configuration(take_bot_last_config())
	reset_bot_stats(False)

pass_values = [2.6, 5.6, 8.8, 12.5]		#Payout: 90%, 80%, 70%, 60%
def simulator_results_screen(idname, name, c_id):
	global simulator_config, config
	error = 'Current payout: ' + str(simulator_config['rend']) + '%'
	at_multiconfig = True
	only_full = False
	commands = []
	print_delay = 100	#ADM
	final_name = 'AVERAGE'
	best = {'winrate': [-1,0,'',0,{}], 
			'profit': [-1,0,'',0,{}], 
			'combo_dif': [-1,0,'',0,{}],
			'stable': [-1,[],'',0,{}],
			'full': [-1,-23,'',0,{}]}	#[ID, best_to, TEXT, TOTAL_BETS, values]

	for key in idname.keys():
		if len(key) > 12:
			commands.append(key)

	if ' → ' in name:
		at_multiconfig = False
		final_name = 'TOTAL'
	else:
		for entry in commands:
			wdl = list(idname[entry]['wdl'])
			combo = list(idname[entry]['combo'])

			if simulator_config['mode'] == 'multi-configs':
				if at_multiconfig:
					if 0 > wdl[0] - wdl[2]:
						wdl.reverse()
						combo.reverse()
				else:
					if 0 > idname['wdl'][0] - idname['wdl'][2]:
						wdl.reverse()
						combo.reverse()

			values = {'winrate': round(wdl[0]*100/max(wdl[2]+wdl[0],1),2),
					'profit': round(wdl[0] - wdl[2],2),
					'combo_dif': combo[0] - combo[1],
					'stable': [0,0,0,0],
					'full': 0}
			for par in idname[entry].keys():
				if par != 'wdl' and par != 'combo':
					if sum(idname[entry][par]['wdl']) <= 0:
						values['full'] -= 1

			for key in ['winrate', 'profit', 'combo_dif', 'full']:
				if values[key] >= best[key][1]:
					change = True
					if values[key] == best[key][1]:
						try:
							if values['profit'] > best[key][4]['profit']:
								pass
							elif values['winrate'] > best[key][4]['winrate']:
								pass
							elif sum(wdl) > best[key][3]:
								pass
							elif values['combo_dif'] > best[key][4]['combo_dif']:
								pass
							else:
								change = False
						except:
							pass

					if change:
						best[key][0] = commands.index(entry)
						best[key][1] = values[key]
						best[key][3] = sum(wdl)
						best[key][4] = values

			#stable
			for par in idname[entry].keys():
				if par != 'wdl' and par != 'combo':
					payout = 0.9
					wdl_par = idname[entry][par]['wdl']
					for i in range(len(values['stable'])):
						x = round( (wdl_par[0]*payout) - wdl_par[2] ,2)
						if x < 0:
							values['stable'][i] += x
						payout -= 0.1

			change = True
			if len(best['stable'][1]) != 0:
				for i in range(len(values['stable'])):
					if values['stable'][i] > best['stable'][1][i]:
						best['stable'][1] = values['stable']
						break
					elif values['stable'][i] == best['stable'][1][i]:
						try:
							if values['profit'] > best[key][4]['profit']:
								pass
							elif values['winrate'] > best[key][4]['winrate']:
								pass
							elif sum(wdl) > best[key][3]:
								pass
							elif values['combo_dif'] > best[key][4]['combo_dif']:
								pass
							else:
								change = False
						except:
							pass

			if change:
				best['stable'][0] = commands.index(entry)
				best['stable'][1] = values['stable']
				best['stable'][3] = sum(wdl)
				best['stable'][4] = values

	while True:
		#LIST
		delay = 0
		text_cluster = []
		
		os.system('cls')
		print('    ID :    NAME     |  BETS  |         W/D/L         | WINRATE | COMBO |   PROFIT   |     STATUS     ')
		print_separator()
		for key in idname.keys():
			if key != 'wdl' and key != 'combo':
				if at_multiconfig:
					id = commands.index(key)
				else:
					id = 0
				pass_var = False
				if only_full and at_multiconfig:
					for par in idname[key].keys():
						if par != 'wdl' and par != 'combo':
							if sum(idname[entry][par]['wdl']) == 0:
								pass_var = True
								break
					if pass_var:
						continue

				wdl = list(idname[key]['wdl'])
				combo = list(idname[key]['combo'])

				if at_multiconfig:
					if 0 > wdl[0] - wdl[2]:
						wdl.reverse()
						combo.reverse()
				else:
					if 0 > idname['wdl'][0] - idname['wdl'][2]:
						wdl.reverse()
						combo.reverse()
				

				if at_multiconfig:
					id_str = str(id) + ': '
				else:
					id_str = ''

				winrate = round(wdl[0]*100/max(wdl[2]+wdl[0],1),2)

				prct = float(abs(winrate-50))
				if pass_values[3] < prct:
					status = 'EXTREME PASS'
				elif pass_values[2] < prct:
					status = 'ULTRA PASS'
				elif pass_values[1] < prct:
					status = 'BIG PASS'
				elif pass_values[0] < prct:
					status = 'PASS'
				else:
					status = 'FAILED'
				
				lucro = round((wdl[0]*(simulator_config['rend']/100)) - (wdl[2]),2)
				if lucro > 0:
					lucro = number_to_limit_str(lucro,11)
					lucro = '+' + lucro
				else:
					lucro = number_to_limit_str(lucro,12)

				#text
				text = ''.join([center_text(id_str, 9), center_text(key, 12), 
					'|', center_text(number_to_limit_str(sum(wdl),8), 8),
					'|', center_text(number_to_limit_str(wdl[0],7)+'/'+number_to_limit_str(wdl[1],7)+'/'+number_to_limit_str(wdl[2],7), 23),
					'|', center_text(str(winrate) + '%', 9),
					'|', center_text(str(combo[0])+'/'+str(combo[1]), 7),
					'|', center_text(lucro, 12),
					'|', center_text(status, 16)
					])

				text_cluster.append(text)	
				if at_multiconfig:
					for b in best.keys():
						if id == best[b][0]:
							best[b][2] = text

				delay -= 1
				if delay < 0:
					print('\n'.join(text_cluster))
					text_cluster.clear()
					delay = print_delay
				id += 1
		print('\n'.join(text_cluster))

		#TOTAL
		wdl = list(idname['wdl'])
		
		if at_multiconfig:
			for x in range(len(wdl)):
				wdl[x] = int(round(wdl[x]/max(len(commands),1),0))

		combo = idname['combo']

		if at_multiconfig == False:
			if 0 > idname['wdl'][0] - idname['wdl'][2]:
				wdl.reverse()
				combo.reverse()

		lucro = round(wdl[0]*simulator_config['rend']/100 - wdl[2],2)
		winrate = round(wdl[0]*100/max(wdl[2]+wdl[0],1),2)

		prct = float(abs(winrate-50))
		if pass_values[3] < prct:
			total_status_text = 'EXTREME PASS'
		elif pass_values[2] < prct:
			total_status_text = 'ULTRA PASS'
		elif pass_values[1] < prct:
			total_status_text = 'BIG PASS'
		elif pass_values[0] < prct:
			total_status_text = 'PASS'
		else:
			total_status_text = 'FAILED'

		if lucro > 0:
			lucro = number_to_limit_str(lucro,11)
			lucro = '+' + lucro
		else:
			lucro = number_to_limit_str(lucro,12)
		
		#text
		print_separator(0)
		print(center_text(final_name, 21) + 
				'|' + center_text(number_to_limit_str(sum(wdl),8), 8) +
				'|' + center_text(number_to_limit_str(wdl[0],7)+'/'+number_to_limit_str(wdl[1],7)+'/'+number_to_limit_str(wdl[2],7), 23) +
				'|' + center_text(str(winrate) + '%', 9) +
				'|' + center_text(str(combo[0])+'/'+str(combo[1]), 7) +
				'|' + center_text(lucro, 12) +
				'|' + center_text(total_status_text, 16)
				)
		
		if at_multiconfig:
			print_separator()
			print(' ♣ BEST WINRATE  ' + best['winrate'][2])
			print(' ♦ BEST PROFIT   ' + best['profit'][2])
			print(' ↕ BEST COMBO DIF' + best['combo_dif'][2])
			print(' ♥ BEST STABLE   ' + best['stable'][2])
			print(' ○ BEST FULL     ' + best['full'][2])

		print_separator(2)
		print(center_text('LOOKING AT SIMULATION: ' + name))
		print_separator()
		print(center_text('\ncommands:    \' = to go back      #NUMBER = to enter a par      -#NUMBER = to change payout(up to 200)'))
		if at_multiconfig == False and simulator_config['mode'] == 'multi-configs':
			print('             add = add configuration')
		elif at_multiconfig:
			print('             of = toggle show only full configs')
		print('')
		print_separator(0)
		print(center_text(error))
		error = ''
		
		choice = input()
		if choice == '\'' or choice == '':
			break
		elif choice == '\'s':
			exit()
		elif at_multiconfig == False and simulator_config['mode'] == 'multi-configs' and choice == 'add':
			configs_path = './data/simulator/multiconfigs/' + simulator_config['mconfiguration'] + '/' 
			config = load_file(configs_path + c_id + '.txt')
			if 0 > idname['wdl'][0] - idname['wdl'][2]:
				config['reverse_movement'] = not config['reverse_movement']
				calculate_config_id()
			check_if_config_exists(config['id'])
		elif at_multiconfig and choice == 'of':
			only_full = not only_full
		elif at_multiconfig and int(choice) >= 0:
			if int(choice) <= len(commands):
				if len(commands[int(choice)]) > 12:
					simulator_results_screen(idname[commands[int(choice)]], 
						name +' → ['+ choice +'] '+ commands[int(choice)][:12], commands[int(choice)])
				else:
					simulator_results_screen(idname[commands[int(choice)]], 
						name + ' → ' + commands[int(choice)], commands[int(choice)])
			else:
				error = 'command number "' + choice + '" isn\'t within scope (max scope is: ' + str(len(commands)) + ')'
		else:
			simulator_config['rend'] = min(abs(int(choice)), 200)
			error = 'setted payout to ' + str(min(abs(int(choice)),200)) + '%'
	load_configuration(take_bot_last_config())

def check_if_config_exists(c_id):
	path = './data/config/' + c_id + '.txt'
	if os.path.isfile(path) == False:
		while True:
			print('Do you want to save this configuration? (Y/N) ', end=' ')
			choice = input()
			if choice.lower() == 'y':
				save_configuration()
				break
			elif choice.lower() == 'n':
				return
	
	while True:
		print('Do you want to make this configuration the current one? (Y/N) ', end=' ')
		escolha = input()
		if escolha.lower() == 'y':
			calculate_config_id()
			path = './data/bot_last_config.txt'
			file = open(path, 'w')
			file.write(config['id'])
			file.close()
			break
		elif escolha.lower() == 'n':
			return


# █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ #

# ▓▓▓▓▓ # #    █████╗ ███╗   ██╗ █████╗ ██╗  ██╗   ██╗███████╗███████╗██████╗ 
#    ▓▓ # #   ██╔══██╗████╗  ██║██╔══██╗██║  ╚██╗ ██╔╝╚══███╔╝██╔════╝██╔══██╗
#    ▓▓ # # # ███████║██╔██╗ ██║███████║██║   ╚████╔╝   ███╔╝ █████╗  ██████╔╝
#    ▓▓ # #   ██╔══██║██║╚██╗██║██╔══██║██║    ╚██╔╝   ███╔╝  ██╔══╝  ██╔══██╗
#    ▓▓ # # # ██║  ██║██║ ╚████║██║  ██║███████╗██║   ███████╗███████╗██║  ██║
# # # # # #   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝
# ----------------------------------------------------------------------------------------------------------------------------- #
		### VARS ###

analyzer_config = {
		'selected': '',
		}

# ----------------------------------------------------------------------------------------------------------------------------- #
		### MENU ###

def save_analyzer_configuration():
	with open('./data/analyzer_configuration.txt', 'wb') as file:
		pickle.dump(analyzer_config, file)

def load_analyzer_configuration():
	global analyzer_config
	path = './data/analyzer_configuration.txt'
	
	if os.path.isfile(path):
		with open(path, 'rb') as file:
			analyzer_config = pickle.load(file)
	else:
		save_analyzer_configuration()

def analyzer_menu():
	load_analyzer_configuration()
	error = ''
	while True:
		print_top_menu_info('ANALYZER')
		print('This analyzes previous simulation and allows to create new and smarter strategies.')
		
		options_array = [
			[1, 'Multi-pattern configuration'],
		]
		
		if analyzer_config['selected'] == '':
			selected_text = '----'
		else:
			selected_text = analyzer_config['selected']

		choice, error = create_options_menu(error, options_array, back_text='Go back to menu', zero_text='Selected: ' + selected_text)
		if choice == '\'':
			break
		elif choice == '0':
			error = analyzer_select()
		elif analyzer_config['selected'] == '':
			error = 'Please select a catalogue in "0" to analyze.'
		elif choice == '1':
			analyzer_multipattern()

# ----------------------------------------------------------------------------------------------------------------------------- #
		### PROGRAM ###

def analyzer_select():
	global analyzer_config
	error = ''
	while True:
		options_array = []
		commands = []
		id = 0
		for dir in list_dirs('data/simulator/rawtest/'):
			options_array.append([int(id), dir])
			commands.append(dir)
			id += 1

		print_top_menu_info('ANALYZER > select')
		print('Select one catalogue to analyze.')

		choice, error = create_options_menu(error, options_array, has_zero=False)
		if choice == '\'':
			return ''
		elif int(choice) <= id and int(choice) > -id:
			analyzer_config['selected'] = commands[int(choice)]
			save_analyzer_configuration()
			return 'Changed select to ' + commands[int(choice)]

def analyzer_multipattern():
	error = ''
	while True:
		mp_status = False
		print_top_menu_info('ANALYZER > multipattern')
		print('This page is responsible to hold anything related to multipattern configurations, which is a smarter strategy that uses the best configuration according to a pattern.')

		options_array = []

		if check_dir('data/analyzer/' + analyzer_config['selected'] + '/'):
			mp_status = True
			options_array = [[1, 'Open multipattern report'], [2, 'Open simplepattern report']]


		choice, error = create_options_menu(error, options_array, zero_text='Create new multipattern')
		if choice == '\'':
			break
		elif choice == '0':
			create_multipattern()
		elif mp_status == True:
			if choice == '1':
				open_multipattern_report('multipattern')
			elif choice == '2':
				open_multipattern_report('simplepattern')

def create_multipattern():
	analyzer_mpresult = {}
	analyzer_mpresult_simple = {}

	best_results = {}
	best_results_simple = {}

	path = 'data/simulator/rawtest/' + analyzer_config['selected'] + '/'
	list_configs = list_dirs(path)
	total_configs = len(list_configs)
	print("Loaded configs: " + str(total_configs))
	done = 0
	for mpconfig in list_configs:
		analyzer_mpresult[mpconfig] = {}
		analyzer_mpresult_simple[mpconfig] = {}
		for betholder in list_files(path + mpconfig):
			for bet in load_file(path + mpconfig + '/' + betholder):
				
				tide = list(bet['tide'])
				for t in range(len(tide)):
					tide[t] = int(round(tide[t], 0))
				tide = str(tide)

				simple = list(bet['tide'])
				for t in range(len(simple)):
					simple[t] = int(round(min(max(simple[t], -1), 1), 0))
				simple = str(simple)

				if tide not in analyzer_mpresult[mpconfig]:
					analyzer_mpresult[mpconfig][tide] = [0,0]
					if tide not in best_results:
						best_results[tide] = ['', 0.0, 0.0, False]		# Config, payout, winrate, reverse
				if simple not in analyzer_mpresult_simple[mpconfig]:
					analyzer_mpresult_simple[mpconfig][simple] = [0,0]
					if simple not in best_results_simple:
						best_results_simple[simple] = ['', 0.0, 0.0, False]

				if bet['result'] == 'WIN':
					analyzer_mpresult[mpconfig][tide][0] += 1
					analyzer_mpresult_simple[mpconfig][simple][0] += 1
				elif bet['result'] == 'LOSS':
					analyzer_mpresult[mpconfig][tide][1] += 1
					analyzer_mpresult_simple[mpconfig][simple][1] += 1
		done += 1
		print(''.join(['(', str(done), '/', str(total_configs), ') ', mpconfig, " done."]))

	# finalize
	print('Calculating best configurations...')
	for mpvar in [[analyzer_mpresult, best_results], [analyzer_mpresult_simple, best_results_simple]]:
		for mpconfig in mpvar[0].keys():
			c = mpvar[0][mpconfig]
			for tide in mpvar[0][mpconfig].keys():
				
				if c[tide][0] > c[tide][1]:
					payout = c[tide][0]*0.9 - c[tide][1]
					winrate = c[tide][0]*100/sum(c[tide])
					reverse = False
				else:
					payout = c[tide][1]*0.9 - c[tide][0]
					winrate = c[tide][1]*100/sum(c[tide])
					reverse = True

				if mpvar[1][tide][1] < payout:
					mpvar[1][tide][0] = config
					mpvar[1][tide][1] = payout
					mpvar[1][tide][2] = winrate
					mpvar[1][tide][3] = reverse

	multipattern = {}
	simplepattern = {}
	for mpvar in [[best_results, multipattern], [best_results_simple, simplepattern]]:
		for tide in mpvar[0].keys():
			if mpvar[0][tide][1] > 0:
				mpvar[1][tide] = mpvar[0][tide]

	# save
	print('All done, saving...')
	path = 'data/analyzer/' + analyzer_config['selected'] + '/'
	check_dir(path)
	save_file(path + 'multipattern.mpconfig', multipattern)
	save_file(path + 'simplepattern.mpconfig', simplepattern)


def open_multipattern_report(mode):
	results = load_file('data/analyzer/' + analyzer_config['selected'] + '/' + mode + '.mpconfig')
	screen = []
	total = {
		'payout': 0,
		'entries': 0,
		'winrate': 0
	}
	if mode == 'multipattern':
		max_entries = 7**5
	else:
		max_entries = 3**5


	print_top_menu_info('ANALYZER > multipattern > ' + mode + ' report')
	for tide in results.keys():
		screen.append(''.join([tide, ': \t', str(int(round(results[tide][1],0))), '\t(', str(round(results[tide][2],1)), '%)\t', str(results[tide][3])]))
		total['payout'] += results[tide][1]
		total['winrate'] = (total['winrate']*total['entries'] + results[tide][2])/(total['entries']+1)
		total['entries'] += 1
	screen.sort()
	print('\n'.join(screen))
	print_separator()
	print('TOTAL ENTRIES:', str(total['entries']), '/', str(max_entries), '(', str(round(total['entries']*100/max_entries,2)), '%)\t\tPAYOUT:', str(int(total['payout'])), '(', str(round(total['winrate'], 2)), '%)')
	input('Type enter to exit report.')


# █████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ #

if __name__ == "__main__":
	multi_progress = Array('i', 6)
	multi_result = Array('i', 24*5)
	reset_config()
	login_accounts()
