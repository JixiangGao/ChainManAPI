# ChainManAPI  
  
  
/get_coins  
>获取所有币种代码更新信息  
>params: commit_num (可选, 默认10)  
>return: 错误  {'code': '1010', 'msg': 'get coins error'}  
>>>成功  {  
>>>>>"BitShares": [  
>>>>>>{  
>>>>>>>"additions": 3771,  
>>>>>>>"author": "Abit",  
>>>>>>>"coin": "BitShares",  
>>>>>>>"collect_time": "Wed, 11 Apr 2018 01:24:26 GMT",  
>>>>>>>"commit_sha": "92eb45cbd3e61c163561b0e6cf7fc99c633e4fcf",  
>>>>>>>"commit_time": "Thu, 29 Mar 2018 03:07:53 GMT",  
>>>>>>>"committer": "GitHub",  
>>>>>>>"content": null,  
>>>>>>>"create_time": "Thu, 29 Mar 2018 03:07:53 GMT",  
>>>>>>>"deletions": 1074,  
>>>>>>>"html_url": "https://github.com/bitshares/bitshares-core/commit/92eb45cbd3e61c163561b0e6cf7fc99c633e4fcf",  
>>>>>>>"repo_name": "bitshares/bitshares-core",  
>>>>>>>"total": 4845  
>>>>>>},  
>>>>>>{  
>>>>>>},  
>>>>>>......  
>>>>>],  
>>>>>"Bitcoin": [  
>>>>>>>......  
>>>>>>],  
>>>>......  
>>>}  
>>>
  
/get_commits_num  
>获取所有币种代码更新数目  
>params: period (天数, 可选, 默认为7)  
>return: 错误	{'code': '1020', 'msg': 'get coins error'}  
>>>成功	{  
>>>>>"BitShares": {  
>>>>>>"additions": 17976,   #增加代码量  
>>>>>>"commits_num": 100,   #提交次数  
>>>>>>"deletions": 6417,    #删减代码量  
>>>>>>"total": 24393        #代码改动总量  
>>>>>},   
>>>>>"Bitcoin": {  
>>>>>>......  
>>>>>},   
>>>>>...  
>>>>>  
>>>>>...  
>>>>} 

/get_last
>获取一个特定币种或全部币种在过去几个时段内，每个时段的更新数目，“时段”的单位是天，周或月
>params: period (枚举类型，为'day','week','month'中的一个，默认为week)
>>>>>>>>>coin (币种的全名，如‘Bitcoin’，‘Bitshares’)
>return：错误	{'code': '1030', 'msg': 'get last error'}
>>>成功 {
>>>"BitShares": [
>>>>{
>>>>>>"additions": 7731, #增加代码量
>>>>>>"commits_num": 13, #提交次数
>>>>>>"deletions": 1965, #删减代码量
>>>>>>"total": 9696, 	 #代码改动总量  
>>>>>>"week": 13		 #今年的第X周， 如果period传入month， 则此项为"month": "2018-03"；如果是day，为"day": "2018-03-29"
>>>>}, 
>>>>{
>>>>>>"additions": 3751, 
>>>>>>"commits_num": 64, 
>>>>>>"deletions": 1742, 
>>>>>>"total": 5493, 
>>>>>>"week": 12
>>>>}, 
>>>>...
>>], 
>>"Bitcoin": [
>>>>...
>>]
>>...
>>}

/get_rank
>获得上周或上月币种的评级，从1-5，为频率从低到高
>params: period (枚举类型，为'week','month'中的一个，默认为week)
>return：错误	{'code': '1040', 'msg': 'get rank error'}
>成功 {
>>>>>  "BitShares": 3, 
>>>>>  "Bitcoin": 2, 
>>>>>  "Bitcoin Cash": 5, 
>>>>>  "Bitcoin Gold": 3, 
>>>>>  "Bytecoin": 4, 
>>>>>  "Cardano": 1, 
>>>>>  ......
>>>>>}