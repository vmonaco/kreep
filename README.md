## kreep: Keystroke Recognition and Entropy Elimination Program

kreep identifies search queries in encrypted network traffic.

See these papers for more details:

    [What Are You Searching For?: A Remote Keylogging Attack on Search Engine Autocomplete](#) (USENIX'19)
    [Feasibility of a Keystroke Timing Attack on Search Engines with Autocomplete](#) (IEEE S&P'19 Workshops)

For background on keylogging side channels, see:
    [Sok: Keylogging side channels](#) (IEEE S&P'18)

### How does it work?

kreep uses several sources of information leakage in client outbound traffic to identify the query. These include:

    1. Autocomplete packets are linearly increasing compared to background traffic.
    2. Percent-encoded URL characters occupy 3 bytes, characters occupy 1 byte.
    3. HTTP2 header compression leaks some information about each character in the query.
    4. Packet timings reveal keydown events in the browser.

## Setup

    $ pip install https://github.com/vmonaco/kreep/archive/master.zip

## Usage

kreep takes a pcap as input. The pcap should contain network traffic to a search engine with autocomplete (only Google and Baidu are currently supported). It prints a list of search query hypothesis. To use the default parameters, provide only the name of the pcap file:

    $ kreep [pcap]

Full usage

    usage: kreep [-h] [--language LANGUAGE] [--bigrams BIGRAMS]
             [--website WEBSITE] [--k K] [--alpha ALPHA]
             pcap

    Keystroke recognition and entropy elimination program

    positional arguments:
      pcap                 filename of the pcap

    optional arguments:
      -h, --help           show this help message and exit
      --language LANGUAGE  filename of the language model (.arpa format)
      --bigrams BIGRAMS    filename of the keystroke timing model (.csv format)
      --website WEBSITE    name of the website. Currently supported are: google,
                           baidu. If not specified, try to guess.
      --k K                number of hypotheses to generate
      --alpha ALPHA        weight of the language model

## Example

    $ kreep examples/example.pcap


## Limitations

    * Currently supported search engines are Google and Baidu
    * Queries must contain only lowercase alphabetic characters and the space key
    * Query words must appear in the language model
    * Victim cannot copy/paste a query, press Delete or Arrow keys, or move the caret in any other way
    * Works only up to the point the victim selects a query from the autocomplete suggestions
