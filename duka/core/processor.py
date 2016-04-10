import lzma
import struct
from datetime import timedelta, datetime

lzma._BUFFER_SIZE = 2048


def decompress_lzma(compressed_buffer):
    return lzma.decompress(compressed_buffer)


def tokenize(buffer):
    token_size = 20
    size = int(len(buffer) / token_size)
    tokens = []
    for i in range(0, size):
        tokens.append(struct.unpack('!IIIff', buffer[i * token_size: (i + 1) * token_size]))
    return tokens


def normalize(day, ticks):
    def norm(time, ask, bid, volume_ask, volume_bid):
        date = datetime(day.year, day.month, day.day) + timedelta(milliseconds=time)
        return date, ask / 100000, bid / 100000, round(volume_ask * 1000000), round(volume_bid * 1000000)

    return list(map(lambda x: norm(*x), ticks))


def decompress(day, compressed_buffer):
    if compressed_buffer.nbytes == 0:
        return compressed_buffer
    return normalize(day, tokenize(decompress_lzma(compressed_buffer)))
