import pqdict
import asyncio
from  pybot.database import query_user_name, query_all_users_profile


rank_pq = pqdict.pqdict(reverse = True)


def rank_init():
    user_tbl = query_all_users_profile()
    for user_dt in user_tbl:
        rank_update(user_dt['uid'], user_dt['coin'])
    return


def rank_update(user_id, coin):
    user = user_id #str(user_id)
    if user in rank_pq:
        rank_pq.updateitem(user, coin)
    else:
        rank_pq.additem(user, coin)
    return


async def rank_list_h2l() -> list:
    rank_list = [] #use list for ordered iteration
    _rank_pq_copy = rank_pq.copy()
    for user in _rank_pq_copy.popkeys():
        user_name = await query_user_name(user)
        if user_name != None:
            rank_list.append((user_name, str(rank_pq[user])))

    return rank_list


def rank_test(update):
    rank_init()
    if update == 1:
        rank_update("user#1", 16)
        rank_update("user#6", 15)
        rank_update("user#9", 1) 
        rank_update("user#7", 14)
        rank_update("user#8", 13)               

    rlist = asyncio.run(rank_list_h2l())
    print(rlist)


if __name__ == '__main__':
    rank_test(1)   
