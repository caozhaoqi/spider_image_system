"""
to be continued
"""
from loguru import logger


@logger.catch
def cal_ys_total(day, is_month, sy, other_ys):
    """
    calculate total ys
    :param sy: 是否dm
    :param day:天数
    :param is_month:是否yk
    :param other_ys: 其他
    :return:ys_total
    """
    if day == '':
        return 0
    if other_ys == '':
        other_ys = 0
    if is_month and sy:
        return day * 150 + 600 + other_ys
    else:
        return day * 60 + 600 + other_ys


@logger.catch
def cal_role_book(level):
    """

    :param level:1->90
    :return:book,moral
    big 419
    middle 1676
    small 8380
    """
    if level == 0:
        return 0, 0, 0, 0, 0
    elif level == 20:
        return 6, 0, 1, 120175, 24000
    elif level == 40:
        return 28, 3, 4, 578325, 120000
    elif level == 50:
        return 29, 0, 0, 579100, 120000
    elif level == 60:
        return 42, 3, 0, 854125, 170000
    elif level == 70:
        return 59, 3, 1, 1195925, 240000
    elif level == 80:
        return 80, 2, 2, 1611875, 320000
    elif level == 90:
        return 171, 0, 4, 3423125, 680000
    else:
        return 419, 0, 0, 120175 + 578325 + 579100 + 854125 + 1195925 + 1611875 + 3423125, \
               (0.24 + 1.2 * 2 + 1.7 + 2.4 + 3.2 + 6.8) * 100000
    # return


@logger.catch
def cal_weapons_materials(star, level):
    """

    :param star: 3 4 5
    :param level: 1->90
    :return:moral,kw
    """
    if star == 3:
        if level == 20:
            return 14925
        elif level == 40:
            return 53450
        elif level == 50:
            return 83250
        elif level == 60:
            return 112500
        elif level == 70:
            return 141750
        elif level == 80:
            return 171000
        elif level == 90:
            return 342450
        else:
            return cal_weapons_materials(3, 20) + cal_weapons_materials(3, 40) + cal_weapons_materials(3, 50) + \
                   cal_weapons_materials(3, 60) + cal_weapons_materials(3, 70) + cal_weapons_materials(3, 80) + \
                   cal_weapons_materials(
                       3, 90)
        # pass
    elif star == 4:
        if level == 20:
            return 22650
        elif level == 40:
            return 86850
        elif level == 50:
            return 148500
        elif level == 60:
            return 210150
        elif level == 70:
            return 271800
        elif level == 80:
            return 333450
        elif level == 90:
            return 666950
        else:
            return cal_weapons_materials(4, 20) + cal_weapons_materials(4, 40) + cal_weapons_materials(4, 50) + \
                   cal_weapons_materials(4, 60) + cal_weapons_materials(4, 70) + cal_weapons_materials(4, 80) + \
                   cal_weapons_materials(
                       4, 90)
        # pass
    elif star == 5:
        if level == 20:
            return 30375
        elif level == 40:
            return 123000
        elif level == 50:
            return 197250
        elif level == 60:
            return 271500
        elif level == 70:
            return 345750
        elif level == 80:
            return 420000
        elif level == 90:
            return 843250
        else:
            return cal_weapons_materials(5, 20) + cal_weapons_materials(5, 40) + cal_weapons_materials(5, 50) + \
                   cal_weapons_materials(5, 60) + cal_weapons_materials(5, 70) + cal_weapons_materials(5, 80) + \
                   cal_weapons_materials(
                       4, 90)
        # pass

    elif level == 1:
        if star == 1:
            return 50000
        elif star == 2:
            return 60000
        elif star == 3:
            return 70000
        elif star == 4:
            return 90000
        elif star == 5:
            return 130000
    return None
    # pass


@logger.catch
def cal_role_talent(level):
    """

    role attack type_num: a e q
    :param level:1->10
    :return:book,mora,cl
    # 3 4 5 2 3 4 z z
    """
    if level == 2:
        return 3, 0, 0, 6, 0, 0, 0, 0, 12500
    elif level == 3:
        return 0, 2, 0, 0, 3, 0, 0, 0, 17500
    elif level == 4:
        return 0, 4, 0, 0, 4, 0, 0, 0, 25000
    elif level == 5:
        return 0, 6, 0, 0, 6, 0, 0, 0, 30000
    elif level == 6:
        return 0, 9, 0, 0, 9, 0, 0, 0, 37500
    elif level == 7:
        return 0, 0, 4, 0, 0, 4, 1, 0, 120000
    elif level == 8:
        return 0, 0, 6, 0, 0, 6, 1, 0, 260000
    elif level == 9:
        return 0, 0, 12, 0, 0, 9, 2, 0, 450000
    elif level == 10:
        return 0, 0, 16, 0, 0, 12, 2, 1, 700000
    return None


@logger.catch
def get_result_str(talent_Q, talent_E, talent_A, small_day_month_card, other_ys_, level, weapon_star, weapon_level):
    """
    return cal result from data
    :param talent_Q:
    :param talent_E:
    :param talent_A:
    :param small_day_month_card:
    :param other_ys_:
    :param level:
    :param weapon_star:
    :param weapon_level:
    :return:
    """
    total_ys = cal_ys_total(small_day_month_card, True, True, other_ys_)
    logger.info("total ys is: " + str(total_ys))
    # logger.info("ck tims is: " + str(total_ys / 160))
    big, middle, small, total_jy, moral = cal_role_book(level)
    weapons_morl = cal_weapons_materials(weapon_star, weapon_level)

    s_b_q, m_b_q, l_b_q, s_c_q, m_c_q, l_c_q, zb_q, hg_q, moral_count_q = cal_role_talent(talent_Q)
    s_b_e, m_b_e, l_b_e, s_c_e, m_c_e, l_c_e, zb_e, hg_e, moral_count_e = cal_role_talent(talent_E)
    s_b_a, m_b_a, l_b_a, s_c_a, m_c_a, l_c_a, zb_a, hg_a, moral_count_a = cal_role_talent(talent_A)
    talent_desc = f', talent update cost matrix: s_b_q, m_b_q, l_b_q, s_c_q, m_c_q, l_c_q, zb_q, hg_q, ' \
                  f'moral_count_q: {s_b_q}, {m_b_q}, {l_b_q}, {s_c_q}, {m_c_q}, {l_c_q}, {zb_q}, {hg_q},' \
                  f' {moral_count_q}; s_b_e, m_b_e, l_b_e, s_c_e, m_c_e, l_c_e, zb_e, hg_e: {s_b_e}, {m_b_e}' \
                  f', {l_b_e}, {s_c_e}, {m_c_e}, {l_c_e}, {zb_e}, {hg_e}; s_b_a, m_b_a, l_b_a, s_c_a, m_c_a, ' \
                  f'l_c_a, zb_a, hg_a, moral_count_a: {s_b_a}, {m_b_a}, {l_b_a}, {s_c_a}, {m_c_a}, {l_c_a}, {zb_a},' \
                  f' {hg_a}, {moral_count_a}; '
    result = "level up need book: big:" + str(big) + ",middle:" + str(middle) + ",small:" + str(
        small) + ",total:" + str(
        total_jy) + ", need moral :" + str(moral) + ", ys: " + str(total_ys) + ", weap moral: " + str(weapons_morl) \
             + talent_desc
    logger.info(result)
    return result


if __name__ == '__main__':
    logger.info("start ys cal system.")
    other = 80 + 80 + 60 + 1000 + 5 * 160
    total_ys = cal_ys_total(30, True, True, other)
    logger.info("total ys is: " + str(total_ys))
    logger.info("ck tims is: " + str(total_ys / 160))
    big, middle, small, total_jy, moral = cal_role_book(0)
    logger.info(
        "level up need book: big:" + str(big) + ", middle:" + str(middle) + ", small: " + str(small) + ", total:" + str(
            total_jy) + ", need moral :" + str(moral))
