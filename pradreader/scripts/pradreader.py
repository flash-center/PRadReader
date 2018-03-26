import pradreader
import argparse

def get_input():
    parser = argparse.ArgumentParser(
                description="")

    parser.add_argument("input_file",
                        action="store", type=str,
                        help="Input file.")

    parser.add_argument("--outname", "-o",
                        action="store", type=str,
                        default="input.txt",
                        help="")

    args = parser.parse_args()

    return(args)


def read_into_PRR():
    args = get_input()
    print(args)
    prad = pradreader.reader.prad(args.input_file)
    prad.read()
    prad.prompt()
    prad.show()
    prad.write(ofile=args.outname)

if __name__=="__main__":
    read_into_PRR()
