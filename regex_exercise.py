import re
import gzip
import csv
import os
from Bio import SeqIO

log_lines = [
    "2024-01-15 10:02:11 INFO Server started on port 8080",
    "2024-01-15 10:03:47 ERROR Failed to connect to database",
    "2024-01-16 08:15:00 WARNING Disk usage at 85%",
    "2024-01-16 14:22:39 ERROR Timeout while fetching https://example.com/api",
    "2024-01-17 09:00:05 INFO User admin logged in from 192.168.1.10",
    "2024-01-17 11:41:18 DEBUG Cache cleared successfully",
    "2024-01-18 03:12:56 ERROR Connection refused from 192.168.1.55",
    "2024-01-18 23:59:02 INFO Backup completed in 42s",
]

# 1 - lines logged on 2024-01-16
print(" Lines from 2024-01-16:")
for line in log_lines:
    if re.search(r"^2024-01-16", line):
        print(line)

# 2 -  lines that are an ERROR or a WARNING
print("\n lines that are an ERROR or a WARNING: ")
for line in log_lines:
    if re.search(r"\b(ERROR|WARNING)\b", line):
        print(line)

#3 - all IPv4 addresses
# (four groups of 1-3 digits separated by dots) that appear anywhere in the log — only 2 of the 8 lines contain one

print( "\n IPv4 addresses that appear anywhere in the log: ")
for line in log_lines:
    ip_adress = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
    for ip in ip_adress:
        print(ip)

#4 - all lines ending in a number of seconds, e.g. ...in 42s
print("\n Lines ending in a number of seconds:")
for line in log_lines:
    if re.search(r"\d+s$", line):
        print(line)

#5 -  all lines that mention a URL (starts with http:// or https://)
print("\n Lines that mention a URL:")
for line in log_lines:
    if re.search(r"https?://", line):
        print(line)

#6 - whether a single line, e.g. log_lines[0], matches the full expected format
# YYYY-MM-DD HH:MM:SS LEVEL message from start to end.
print("\n All lines match the full expected format: ")
full_format_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} (INFO|ERROR|WARNING|DEBUG) .+"
match = re.fullmatch(full_format_pattern, log_lines[0])
print(bool(match))


#--------------------------------- TASK 2 ------------------------------------
print("\n ____________________ TASK 2 _________________________________")
def reverse_complement(sequence):
    complement_map = {"A": "T", "T": "A", "C": "G", "G": "C"}
    complemented = "".join(complement_map[base] for base in sequence)
    return complemented[::-1]


class SequencingRead:
    def __init__(self, read_id, sequence):
        self.read_id = read_id
        self.sequence = sequence

    def matches_mid_pair(self, forward_mid, reverse_mid):
        reverse_mid_rc = reverse_complement(reverse_mid)
        pattern = r"^" + forward_mid + r".*" + reverse_mid_rc + r"$"
        return bool(re.match(pattern, self.sequence))

    def trim_mid_pair(self, forward_mid, reverse_mid):
        if not self.matches_mid_pair(forward_mid, reverse_mid):
            return None
        reverse_mid_rc = reverse_complement(reverse_mid)
        insert = self.sequence[len(forward_mid): len(self.sequence) - len(reverse_mid_rc)]
        return insert

    def describe(self):
        return f"SequencingRead {self.read_id} ({len(self.sequence)} bp)"


if __name__ == "__main__":
    r1 = SequencingRead("demo_1", "AGCTTCGA" + "N" * 20 + reverse_complement("TGCAGGTC"))
    print(r1.describe())
    print(r1.matches_mid_pair("AGCTTCGA", "TGCAGGTC"))
    print(r1.matches_mid_pair("CGATCGAT", "GCTAGCTA"))
    print(r1.trim_mid_pair("AGCTTCGA", "TGCAGGTC"))






#--------------------------------- TASK 3 ------------------------------------
print("\n ____________________ TASK 3 _________________________________")
class Demultiplexer:
    def __init__(self, fasta_path, mid_table_path):
        self.reads = []
        with gzip.open(fasta_path, "rt") as handle:
            for record in SeqIO.parse(handle, "fasta"):
                self.reads.append(SequencingRead(record.id, str(record.seq)))

        self.samples = []
        with open(mid_table_path) as handle:
            reader = csv.DictReader(handle, delimiter=";")
            for row in reader:
                label = f"{row['SampleID']}_{row['Description']}"
                forward_mid = row["FBarcodeSequence"]
                reverse_mid = row["RBarcodeSequence"]
                self.samples.append((label, forward_mid, reverse_mid))

        self.assigned = {label: [] for label, forward_mid, reverse_mid in self.samples}
        self.unassigned = []

    def assign_reads(self):
        for read in self.reads:
            assigned_this_read = False

            for label, forward_mid, reverse_mid in self.samples:
                # sense orientation: starts with forward_mid
                if read.matches_mid_pair(forward_mid, reverse_mid):
                    trimmed_sequence = read.trim_mid_pair(forward_mid, reverse_mid)
                    self.assigned[label].append(SequencingRead(read.read_id, trimmed_sequence))
                    assigned_this_read = True
                    break

                # antisense orientation: starts with reverse_mid instead
                if read.matches_mid_pair(reverse_mid, forward_mid):
                    trimmed_sequence = read.trim_mid_pair(reverse_mid, forward_mid)
                    self.assigned[label].append(SequencingRead(read.read_id, trimmed_sequence))
                    assigned_this_read = True
                    break

            if not assigned_this_read:
                self.unassigned.append(read)

    def report(self):
        lines = []
        for label, reads in self.assigned.items():
            lines.append(f"{label}\t{len(reads)}")
        lines.append(f"unassigned\t{len(self.unassigned)}")
        return "\n".join(lines)

    def write_fasta(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        for label, reads in self.assigned.items():
            if len(reads) == 0:
                continue
            output_path = os.path.join(output_dir, f"{label}.fasta")
            with open(output_path, "w") as out_file:
                for read in reads:
                    out_file.write(f">{read.read_id}\n{read.sequence}\n")


if __name__ == "__main__":

    demux = Demultiplexer("fishes.fna.gz", "fishes_MIDs.csv")
    demux.assign_reads()
    print(demux.report())
    demux.write_fasta("demux_output")


