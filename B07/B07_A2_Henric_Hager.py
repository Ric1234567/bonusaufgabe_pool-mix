# Henric Hager, 1881834; Philipp Schwabenbauer, 1841362

# Aufgabe 3
import random
import string

# create attack log
attack_log = open("attack.log", "w")


# f.write("Now the file has more content!")
# f.close()

class PoolMix:
    def __init__(self, name, batch_size, pool_size, follow_mix):
        self.name = name
        self.batch = []
        self.pool = []
        self.batch_size = batch_size
        self.pool_size = pool_size
        self.follow_mix = follow_mix

    def process(self):
        if self.pool_size + self.batch_size <= len(self.batch) + len(self.pool):
            all_messages = self.batch + self.pool

            rnd_messages = []
            # select random Messages
            for m in range(self.batch_size):
                rnd_int = random.randint(0, len(all_messages) - 1)
                rnd_messages.append(all_messages[rnd_int])
                all_messages.pop(rnd_int)

            random.shuffle(rnd_messages)

            # remove sent messages
            self.batch.clear()
            self.pool.clear()
            self.pool += all_messages

            if rnd_messages is not None:
                # mix sends messages
                if self.follow_mix is not None:
                    # mix is not the last one in cascade
                    print(self.name + " sends " + str(len(rnd_messages)) + " Messages: " + str(
                        rnd_messages) + " to " + str(self.follow_mix.name))
                    self.follow_mix.add_messages(rnd_messages)
                else:
                    print(self.name + " sends " + str(len(rnd_messages)) + " Messages: " + str(
                        rnd_messages) + " to receivers")

            return rnd_messages

    def add_message(self, message):
        if message is not None:
            if len(self.pool) < self.pool_size:
                self.pool.append(message)
            elif len(self.batch) < self.batch_size:
                self.batch.append(message)
            else:
                # mix full; clear batch before adding message
                self.process()
                self.batch.append(message)

    def add_messages(self, messages):
        for mess in messages:
            self.add_message(mess)

    def __str__(self):
        return "Mix content:\nBatch: " + str(self.batch) + "\nPool: " + str(self.pool)


class Message:
    def __init__(self, timestamp, sender, receiver):
        self.timestamp = timestamp
        self.sender = sender
        self.receiver = receiver

    def __str__(self):
        return '[Message: Sender:' + str(self.sender) + ' Receiver:' + str(self.receiver) + ']'

    def __repr__(self):
        return str(self)


# Simulation a)---------------------------------------------------------------------------------------------------------
print("Teilaufgabe a)")
mix = PoolMix("PoolMix", 4, 2, None)
for i in range(100):
    # print round nr
    print('Round', i)

    # log
    attack_log.write("Round " + str(i) + ":\n")

    # random sender sends message to mix
    rnd_sender = random.randint(0, 10)
    rnd_receiver = random.randint(0, 5)
    print("Sender", rnd_sender, "sends Message to mix.")
    attack_log.write("[Input] Mix receives a message from Sender " + str(rnd_sender) + "!\n")

    # add to mix
    mix.add_message(Message(i, rnd_sender, rnd_receiver))

    # print current mix batch and pool
    print(mix)

    # send messages
    sent_messages = mix.process()
    if sent_messages is not None:
        # log attacker
        # print("Mix sends " + str(len(sent_messages)) + " Messages: " + str(sent_messages))
        for message in sent_messages:
            attack_log.write("[Output] Mix sends a message to Receiver " + str(message.receiver) + "\n")

        # print new content
        print("New " + str(mix))

    print()

attack_log.close()

# b)---------------------------------------------------------------------------------------------------------
print("Teilaufgabe b)")

# read message of file
file = open('messages.txt', 'r')
message_list = []
lines = file.readlines()
for i in range(1, 1000):
    line = lines[i].split()
    message_list.append(Message(line[0], line[1], line[2]))


def simulation(mixes):
    # Simulation 1. Variant ------------------------------------------------------------------------------------
    round_nr = 0
    for message in message_list:
        print("Round " + str(round_nr))
        print("Sender " + message.sender + " sends message to receiver " + message.receiver)

        # add new message to first mix
        mixes[0].add_message(message)

        # mix sends to following mix in cascade
        for i in range(len(mixes)):
            mixes[i].process()
            # if sent_messages is not None:
            # if mixes[i] is not mixes[-1]:  # if not the last one
            # print("Mix-" + str(i) + " sends " + str(sent_messages) + " to Mix-" + str(i + 1))
            # mixes[i + 1].add_messages(sent_messages)
            # else:
            # print("Mix-" + str(i) + " sends " + str(sent_messages) + " to receivers")
            # else:
            #     break

        round_nr += 1
        print()


print("1. Variante")
mix3 = PoolMix("Mix-3", 3, 0, None)
mix2 = PoolMix("Mix-2", 3, 0, mix3)
mix1 = PoolMix("Mix-1", 3, 0, mix2)
simulation([mix1, mix2, mix3])

print("2. Variante")
mix3 = PoolMix("Mix-3", 3, 2, None)
mix2 = PoolMix("Mix-2", 3, 2, mix3)
mix1 = PoolMix("Mix-1", 3, 2, mix2)
simulation([mix1, mix2, mix3])

print("3. Variante")
mix3 = PoolMix("Mix-3", 3, 6, None)
mix2 = PoolMix("Mix-2", 3, 2, mix3)
mix1 = PoolMix("Mix-1", 3, 0, mix2)
simulation([mix1, mix2, mix3])
