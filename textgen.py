import spacy
import markovify
from pythonosc import udp_client
import argparse
import threading

#OSC client setup
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
                        help="The ip of the OSC server")
    parser.add_argument("--port2", default=12000,
                        help="The port the OSC server is listening on")
    parser.add_argument("--port", type=int, default=7400,
                        help="The port the OSC server is listening on")
    args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)
clients = udp_client.SimpleUDPClient(args.ip, args.port2)

#load text file
def loadtext():

    print("sorting file")
    global text
    with open("corpus") as corpus_file:
        text = corpus_file.read()


def accgen():
    global generator_2

    print("loading nlp")
    nlp = spacy.load("en_core_web_sm")
    print("parsing")
    text_doc = nlp(text)

    print("converting")
    text_sents = ' '.join([sent.text for sent in text_doc.sents if len(sent.text) > 1])

    print("POSifying")
    class POSifiedText(markovify.Text):
        def word_split(self, sentence):
            return ['::'.join((word.orth_, word.pos_)) for word in nlp(sentence)]

        def word_join(self, words):
            sentence = ' '.join(word.split('::')[0] for word in words)
            return sentence

    generator_2 = POSifiedText(text_sents, state_size=3)


def generateacc():

    threading.Timer(10.0, generateacc).start()
    for i in range(1):
        markovsent2 = (generator_2.make_short_sentence(max_chars=150))
        client.send_message("/markov", markovsent2)
        print(markovsent2)

def generatefast():
    threading.Timer(10.0, generatefast).start()
    for i in range(1):
        text_model = markovify.Text(text)
        markovsent2 = (text_model.make_short_sentence(max_chars=150))
        client.send_message("/markov", markovsent2)
        print(markovsent2)


loadtext()
#comment out the generator which you don't want to use



#this generator acts faster but is less accurate when it comes to grammar and sense - arguably more interesting results even thought a few non-sensical ones.
#unlimited corpus file chars

# fastgen()
# generatefast()

#this generator is more accurate but takes longer to work. It also tends to feed out entire sentences found in the text if the corpus file is shorter.
#may also give you 'none' if source text is shorter
#max corpus file 100000 chars
accgen()
generateacc()