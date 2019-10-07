class PacketEnum(object):
    PACKET_BUFFER_SIZE = 48 * 1024
    PACKET_SEND_BUFFER_SIZE = 64 * 1024

    SERVER = "127.0.0.1"
    PORT = 6600
    PACKET_VERSION = 20101

    # PACKET_HEADER
    PACKET_HEADER_TYPE_POS = 0
    PACKET_HEADER_TYPE_SIZE = 1

    PACKET_HEADER_VERSION_POS = 1
    PACKET_HEADER_VERSION_SIZE = 4

    PACKET_HEADER_LEN_POS = 5
    PACKET_HEADER_LEN_SIZE = 4

    # PACKET_BODY
    PACKET_BODY_ID_POS = 9
    PACKET_BODY_ID_SIZE = 8

    PACKET_BODY_START_TIME_POS = 17
    PACKET_BODY_START_TIME_SIZE = 8

    PACKET_BODY_ELAPSED_POS = 25
    PACKET_BODY_ELAPSED_SIZE = 4

    PACKET_BODY_CPU_POS = 29
    PACKET_BODY_CPU_SIZE = 8

    PACKET_BODY_MEMOERY_POS = 37
    PACKET_BODY_MEMOERY_SIZE = 8

    PACKET_BODY_THREAD_ID_POS = 45
    PACKET_BODY_THREAD_ID_SIZE = 8

    PACKET_BODY_TRACE_DATA_POS = 53

    # PACKET_SIZE
    PACKET_HEADER_SIZE = PACKET_HEADER_TYPE_SIZE + PACKET_HEADER_VERSION_SIZE + PACKET_HEADER_LEN_SIZE
    PACKET_BODY_REQUIRED_SIZE = PACKET_BODY_ID_SIZE + PACKET_BODY_START_TIME_SIZE + PACKET_BODY_ELAPSED_SIZE \
                + PACKET_BODY_CPU_SIZE + PACKET_BODY_MEMOERY_SIZE + PACKET_BODY_THREAD_ID_SIZE
