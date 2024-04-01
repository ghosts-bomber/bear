import logging
def GetAvgAndSigma(arr):
    if len(arr) == 0:
        return (0, 0)
    avg = sum(arr) / len(arr)
    sigma = 0
    for x in arr:
        sigma += (x - avg)**2
    sigma /= len(arr)
    sigma = sigma**0.5
    return (avg, sigma)


def ConvertStrToTime(timeStr: str):
    temp = timeStr.split(':')
    return int(temp[0]) * 3600 + int(temp[1]) * 60 + int(temp[2])


def ConvertStrToTimePrecise(timeStr: str):
    temp = timeStr.split(':')
    return float(temp[0]) * 3600 + float(temp[1]) * 60 + float(temp[2])


def ConvertTimeToStr(time: int) -> str:
    hour = time // 3600
    time %= 3600
    minute = time // 60
    time %= 60
    return '%2s:%2s:%2s' % (str(hour).zfill(2), str(minute).zfill(2),
                            str(time).zfill(2))


def FormatedPrint(content, totalLength=50) -> str:
    if len(content) > totalLength:
        totalLength = len(content) + 12
    left = right = (totalLength - len(content) - 4) // 2
    if (totalLength - len(content)) % 2 == 1:
        right += 1
    logging.info(f'[{"-"*left} {content} {"-"*right}]')


def ConvertUnixTimeToStr(time: float) -> str:
    second = int(round(time % (3600 * 24), 0)) + 3600 * 8
    return ConvertTimeToStr(second)


def ConvertGearToNumber(gear: str) -> int:
    if gear == 'NEUTRAL':
        return 0
    elif gear == 'DRIVE':
        return 1
    elif gear == 'REVERSE':
        return -1
    else:
        return 666


def ConvertNumberToGear(n: int) -> str:
    if n == 0:
        return 'NEUTRAL'
    elif n == 1:
        return 'DRIVE'
    elif n == -1:
        return 'REVERSE'
    else:
        return 'ERROR'


def GetMinMaxFromMultipleLists(arr):
    mn = 2**63
    mx = -mn

    for subarr in arr:
        if len(subarr) != 0:
            mn = min(mn, min(subarr))
            mx = max(mx, max(subarr))

    return int(mn), int(mx)
