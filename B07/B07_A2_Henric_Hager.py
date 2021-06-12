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

    # processes the internal messages in batch and pool and sends them to the receivers if the sending condition is true
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

            # random output order
            random.shuffle(selected_to_send_messages)

            # remove sent messages
            self.batch.clear()
            self.pool.clear()
            self.pool += all_messages

            if selected_to_send_messages is not None:
                # send all messages to their addresses
                for m in selected_to_send_messages:
                    send_message(m)

            return selected_to_send_messages

    # removes the address part of the message to get the next receiver
    @staticmethod
    def decrypt_message_content(message):
        return message.content

    # adds a message to the internal mix storage (batch or pool)
    def add_message(self, message):
        if message is not None:
            dec_message = self.decrypt_message_content(message)

            # first check if pool has space available
            if len(self.pool) < self.pool_size:
                self.pool.append(dec_message)
            # check if batch has space available
            elif len(self.batch) < self.batch_size:
                self.batch.append(dec_message)

            # no else part here because every time a new message arrives the Mix processes all messages and
            # if it is full, the messages are sent

            return self.process()

    def age_messages(self, index):
        all_messages = self.pool + self.batch
        for m in all_messages:
            # add it to the most inner message
            inner_message = m.get_inner_message()
            inner_message.time_in_mix[index] += 1

    def __str__(self):
        return self.name + ":{\n\tBatch(" + str(len(self.batch)) + "): " + str(self.batch) + "\n\tPool(" + str(
            len(self.pool)) + "): " + str(self.pool) + "}"


class Message:
    def __init__(self, timestamp, sender, receiver, content, mix_amount=0):
        self.timestamp = timestamp
        self.sender = sender
        self.receiver = receiver
        self.content = content

        # init; position is the position of the mix in the cascade
        self.time_in_mix = [1] * mix_amount

    # gets the most inner message of a top-message
    def get_inner_message(self):
        tmp = self
        while True:
            if type(tmp.content) is Message:
                tmp = tmp.content
            else:
                return tmp

    def get_sender_name(self):
        # sender name
        if type(self.sender) is PoolMix:
            return self.sender.name
        else:
            return self.sender

    def get_receiver_name(self):
        # receiver name
        if type(self.receiver) is PoolMix:
            return self.receiver.name
        else:
            return self.receiver

    def __str__(self):
        return '{ Msg: {Ts:' + str(self.timestamp) + '; Snd:' + str(self.get_sender_name()) + '; Rec:' + str(
            self.get_sender_name()) + '; Cnt:{' + str(
            self.content) + '}} }'

    def __repr__(self):
        return str(self)


# reads the messages.txt in
def read_in_generic_messages():
    # read message of file
    file = open('messages.txt', 'r')
    message_list = []
    lines = file.readlines()
    for i in range(1, 1001):
        line = lines[i].split()
        message_list.append(Message(line[0], line[1], line[2], None))

    return message_list


# creates a message in the format: A1,c(A2,c(...))
def create_mix_message(message: Message, mixes):
    tmp_message = Message(message.timestamp, mixes[-1], message.receiver, "some secret text", len(mixes))

    if len(mixes) == 1:
        return Message(message.timestamp, message.sender, mixes[0],
                       Message(message.timestamp, mixes[0], message.receiver, "some secret text", len(mixes)))

    # reverse loop
    for i in range(len(mixes), 0, -1):
        if i - 2 >= 0:
            # sender is a mix
            tmp_message = Message(message.timestamp, mixes[i - 2], mixes[i - 1], tmp_message)
        else:
            # logical sender; first message from non-mix to mix
            tmp_message = Message(message.timestamp, message.sender, mixes[i - 1], tmp_message)
    return tmp_message


# sends a message to the receiver address in the message itself
def send_message(message: Message):
    print(str(message.get_sender_name()) + " sends " + str(message) + " to " + str(message.get_receiver_name()))
    if type(message.receiver) is PoolMix:
        return message.receiver.add_message(message)


# starts a simulation of a mix-cascade
def simulation(mixes, message_list):
    round_nr = 0
    message_sink = []  # all messages will end up here to perform later calculations (Teilaufgabe c))

    # iterate the generic_messages from message.txt
    for generic_message in message_list:
        print("Round " + str(round_nr))

        # sender creates mix message: A1, Content(A2, Content(A3, Content(...)))
        mix_message = create_mix_message(generic_message, mixes)

        # send the first message
        messages_sent = send_message(mix_message)

        # add to message sink to perform later calculations (Teilaufgabe c))
        if messages_sent is not None:
            for m in messages_sent:
                message_sink.append(m.get_inner_message())

        print()
        print("Mix status:")
        for i, mix in enumerate(mixes):
            # print status of single mix
            print(str(mix))

            # age all messages from mix
            mix.age_messages(i)

        round_nr += 1
        print(
            "-------------------------------------------------------------------------------------------------------")
        print()
    print("Simulation done!")
    return message_sink


# draws hists and prints "Average sending time per message"
def calc_stats(messages, mixes, variant):
    for i, mix in enumerate(mixes):
        # get all ages per mix
        tmp = []
        for m in messages:
            tmp.append(m.time_in_mix[i])

        # calc mean
        mean_mix = stat.mean(tmp)

        if max(tmp) > 0:
            # draw hist
            plt.hist(tmp, max(tmp), edgecolor='black', align='mid')
            plt.title(
                "Average time per mix\n" + variant + ", " + mix.name + ", Mean_Mix=" + str("{:.2f}".format(mean_mix)))
            plt.show()

    print(
        "Average sending time per message: " + str("{:.2f}".format(calc_mean_sender_to_receiver(messages, len(mixes)))))


# calculates the "Average sending time per message"
def calc_mean_sender_to_receiver(messages, mix_amount):
    data = []
    for m in messages:
        tmp = 0
        # add together sending time per mix
        for i in range(mix_amount):
            tmp += m.time_in_mix[i]
        data.append(tmp)

    # return mean
    return stat.mean(data)


# read message.txt
m_list = read_in_generic_messages()

# Simulation a)---------------------------------------------------------------------------------------------------------
print("Teilaufgabe a)")
mix1 = PoolMix("Mix-1", 4, 2)
mixes = [mix1]
messages = simulation(mixes, m_list)
calc_stats(messages, mixes, "a)")

# Simulation b)---------------------------------------------------------------------------------------------------------
print()
print("===============================================================================================")
print("Teilaufgabe b)")
print("1. Variante ===============================================================================================")
mix3 = PoolMix("Mix-3", 3, 0)
mix2 = PoolMix("Mix-2", 3, 0)
mix1 = PoolMix("Mix-1", 3, 0)
mixes = [mix1, mix2, mix3]
messages = simulation(mixes, m_list)
calc_stats(messages, mixes, "1.Variante")

print("2. Variante ===============================================================================================")
mix3 = PoolMix("Mix-3", 3, 2)
mix2 = PoolMix("Mix-2", 3, 2)
mix1 = PoolMix("Mix-1", 3, 2)
mixes = [mix1, mix2, mix3]
messages = simulation(mixes, m_list)
calc_stats(messages, mixes, "2.Variante")

print("3. Variante ===============================================================================================")
mix3 = PoolMix("Mix-3", 3, 6)
mix2 = PoolMix("Mix-2", 3, 2)
mix1 = PoolMix("Mix-1", 3, 0)
mixes = [mix1, mix2, mix3]
messages = simulation(mixes, m_list)
calc_stats(messages, mixes, "3.Variante")
