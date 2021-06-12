# Henric Hager, 1881834; Philipp Schwabenbauer, 1841362

# Aufgabe 3
import random
import matplotlib.pyplot as plt
import statistics as stat


class PoolMix:
    def __init__(self, name, batch_size, pool_size):
        self.name = name
        self.batch = []
        self.pool = []
        self.batch_size = batch_size
        self.pool_size = pool_size

    def process(self):
        # check if mix is full
        if self.pool_size + self.batch_size <= len(self.batch) + len(self.pool):
            all_messages = self.batch + self.pool

            selected_to_send_messages = []
            # select random Messages
            for m in range(self.batch_size):
                rnd_int = random.randint(0, len(all_messages) - 1)
                selected_to_send_messages.append(all_messages[rnd_int])
                all_messages.pop(rnd_int)

            random.shuffle(selected_to_send_messages)

            # remove sent messages
            self.batch.clear()
            self.pool.clear()
            self.pool += all_messages

            if selected_to_send_messages is not None:
                # send all messages to address
                for m in selected_to_send_messages:
                    if type(m.receiver) is PoolMix:
                        # send to other mix
                        m.receiver.add_message(m)
                        print(self.name + " sends " + str(m) + " to " + str(m.receiver.name))
                    else:
                        # sent to logical receiver
                        print(self.name + " sends " + str(m) + " to " + str(m.receiver))

            return selected_to_send_messages

    @staticmethod
    def decrypt_message_content(message):
        return message.content

    def add_message(self, message):
        if message is not None:
            dec_message = self.decrypt_message_content(message)

            if len(self.pool) < self.pool_size:
                self.pool.append(dec_message)
            elif len(self.batch) < self.batch_size:
                self.batch.append(dec_message)

            return self.process()

    def add_time_round(self, index):
        all_messages = self.pool + self.batch
        for m in all_messages:
            inner_message = m.get_inner_message()
            inner_message.time_in_mix_counter[index] += 1

    def __str__(self):
        return self.name + ":{\nBatch(" + str(len(self.batch)) + "): " + str(self.batch) + "\nPool(" + str(
            len(self.pool)) + "): " + str(self.pool) + "}"


class Message:
    def __init__(self, timestamp, sender, receiver, content, mix_amount=0):
        self.timestamp = timestamp
        self.sender = sender
        self.receiver = receiver
        self.content = content

        # init
        self.time_in_mix_counter = [1] * mix_amount

    def get_inner_message(self):
        tmp = self
        while True:
            if type(tmp.content) is Message:
                tmp = tmp.content
            else:
                return tmp

    def __str__(self):
        # sender name
        if type(self.sender) is PoolMix:
            print_snd = self.sender.name
        else:
            print_snd = self.sender

        # receiver name
        if type(self.receiver) is PoolMix:
            print_rec = self.receiver.name
        else:
            print_rec = self.receiver

        return '{ Msg: {Ts:' + str(self.timestamp) + '; Snd:' + str(print_snd) + '; Rec:' + str(
            print_rec) + '; Cnt:{' + str(
            self.content) + '}} }'

    def __repr__(self):
        return str(self)


def read_in_generic_messages():
    # read message of file
    file = open('messages.txt', 'r')
    message_list = []
    lines = file.readlines()
    for i in range(1, 1001):
        line = lines[i].split()
        message_list.append(Message(line[0], line[1], line[2], None))

    return message_list


def create_mix_message(message: Message, mixes):
    tmp_message = Message(message.timestamp, mixes[-1], message.receiver, "some secret text", len(mixes))

    # reverse loop
    for i in range(len(mixes), 0, -1):
        if i - 2 >= 0:
            # mix is sender
            tmp_message = Message(message.timestamp, mixes[i - 2], mixes[i - 1], tmp_message)
        else:
            # original sender
            tmp_message = Message(message.timestamp, message.sender, mixes[i - 1], tmp_message)
    return tmp_message


def simulation(mixes, message_list):
    round_nr = 0
    message_sink = []

    for generic_message in message_list:
        print("Round " + str(round_nr))

        # sender creates mix message: A1, Content(A2, Content(A3, Content(...)))
        mix_message = create_mix_message(generic_message, mixes)
        print(
            "Sender " + mix_message.sender + " sends " + str(mix_message) + " to " + str(mix_message.receiver.name))

        # add new message to first mix
        messages_sent = mixes[0].add_message(mix_message)
        if messages_sent is not None:
            for m in messages_sent:
                message_sink.append(m.get_inner_message())

        # mix sends to following mix in cascade
        # for i in range(len(mixes)):
        #     mixes[i].process()

        print()
        print("Mix status:")
        for i, mix in enumerate(mixes):
            # print status of single mix
            print(str(mix))

            # processing time
            mix.add_time_round(i)

        round_nr += 1
        print(
            "-------------------------------------------------------------------------------------------------------")
        print()
    print("simulation done")
    return message_sink


def draw_hist(messages, mixes, variant):
    for i, mix in enumerate(mixes):
        tmp = []
        for m in messages:
            tmp.append(m.time_in_mix_counter[i])

        # calc avg
        mean_mix = stat.mean(tmp)

        if max(tmp) > 0:
            # draw hist
            plt.hist(tmp, max(tmp), edgecolor='black', align='mid')
            plt.title(
                "Average time per mix\n" + variant + ", " + mix.name + ", Mean_Mix=" + str("{:.2f}".format(mean_mix)))
            plt.show()

    print(
        "Average sending time per message: " + str("{:.2f}".format(calc_mean_sender_to_receiver(messages, len(mixes)))))


def calc_mean_sender_to_receiver(messages, mix_amount):
    data = []
    for m in messages:
        tmp = 0
        for i in range(mix_amount):
            tmp += m.time_in_mix_counter[i]
        data.append(tmp)

    return stat.mean(data)


m_list = read_in_generic_messages()

# Simulation a)---------------------------------------------------------------------------------------------------------
print("Teilaufgabe a)")
mix1 = PoolMix("Mix-1", 4, 2)
mixes = [mix1]
# messages = simulation(mixes, m_list)
# draw_hist(messages, mixes, "a)")

# b)---------------------------------------------------------------------------------------------------------
print()
print("===============================================================================================")
print("Teilaufgabe b)")
print("1. Variante ===============================================================================================")
mix3 = PoolMix("Mix-3", 3, 0)
mix2 = PoolMix("Mix-2", 3, 0)
mix1 = PoolMix("Mix-1", 3, 0)
mixes = [mix1, mix2, mix3]
messages = simulation(mixes, m_list)
draw_hist(messages, mixes, "1.Variante")

print("2. Variante ===============================================================================================")
mix3 = PoolMix("Mix-3", 3, 2)
mix2 = PoolMix("Mix-2", 3, 2)
mix1 = PoolMix("Mix-1", 3, 2)
mixes = [mix1, mix2, mix3]
messages = simulation(mixes, m_list)
draw_hist(messages, mixes, "2.Variante")

print("3. Variante ===============================================================================================")
mix3 = PoolMix("Mix-3", 3, 6)
mix2 = PoolMix("Mix-2", 3, 2)
mix1 = PoolMix("Mix-1", 3, 0)
mixes = [mix1, mix2, mix3]
messages = simulation(mixes, m_list)
draw_hist(messages, mixes, "3.Variante")
