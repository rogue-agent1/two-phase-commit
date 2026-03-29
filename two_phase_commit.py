#!/usr/bin/env python3
"""two_phase_commit - Two-phase commit protocol for distributed transactions."""
import sys

class Participant:
    def __init__(self, name, will_fail=False):
        self.name = name
        self.will_fail = will_fail
        self.state = "init"
        self.log = []
    def prepare(self, txn_id):
        self.log.append(("prepare", txn_id))
        if self.will_fail:
            self.state = "aborted"
            return False
        self.state = "prepared"
        return True
    def commit(self, txn_id):
        self.log.append(("commit", txn_id))
        self.state = "committed"
    def abort(self, txn_id):
        self.log.append(("abort", txn_id))
        self.state = "aborted"

class Coordinator:
    def __init__(self, participants):
        self.participants = participants
        self.log = []
    def execute(self, txn_id):
        # Phase 1: Prepare
        self.log.append(("begin", txn_id))
        votes = []
        for p in self.participants:
            vote = p.prepare(txn_id)
            votes.append((p.name, vote))
        self.log.append(("votes", votes))
        # Phase 2: Commit or Abort
        if all(v for _, v in votes):
            self.log.append(("decision", "commit"))
            for p in self.participants:
                p.commit(txn_id)
            return True
        else:
            self.log.append(("decision", "abort"))
            for p in self.participants:
                if p.state == "prepared":
                    p.abort(txn_id)
            return False

def test():
    # all succeed
    p1, p2, p3 = Participant("db1"), Participant("db2"), Participant("db3")
    coord = Coordinator([p1, p2, p3])
    assert coord.execute("tx1") == True
    assert all(p.state == "committed" for p in [p1, p2, p3])
    # one fails
    p4 = Participant("db4")
    p5 = Participant("db5", will_fail=True)
    p6 = Participant("db6")
    coord2 = Coordinator([p4, p5, p6])
    assert coord2.execute("tx2") == False
    assert p5.state == "aborted"
    assert p4.state == "aborted"  # rolled back
    # coordinator log
    assert ("decision", "abort") in coord2.log
    print("OK: two_phase_commit")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: two_phase_commit.py test")
