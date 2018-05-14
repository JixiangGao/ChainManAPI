import result
import config


new_coins = result.coins
config_info = config.info

count = 0

for coin in new_coins:
	coin_name = coin['coin_short_name']
	flag=0
	for i in config_info:
		if coin_name.lower() == i['coin_short_name'].lower():
			flag=1
			break
	if flag == 0:
		coin['coin_short_name'] = coin_name.upper()
		print(str(coin)+',')
				
for coin in config_info:
	print(str(coin)+',')
	count += 1;
			
print(count)
