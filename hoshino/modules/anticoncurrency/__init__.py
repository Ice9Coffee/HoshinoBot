class Process_Monitor:
    def __init__(self, gid, trigger_group_index, trigger_word, process_status_dict):
        self.gid = gid
        self.trigger_group_index = trigger_group_index
        self.trigger_word = trigger_word
        self.process_status_dict = process_status_dict

    def __enter__(self):
        if (self.gid, self.trigger_group_index) in self.process_status_dict:
            self.process_status_dict[(self.gid, self.trigger_group_index)].append(self.trigger_word)
        else:
            self.process_status_dict[(self.gid, self.trigger_group_index)] = [self.trigger_word]
        return self

    def __exit__(self, type_, value, trace):
        if self.trigger_word in self.process_status_dict[(self.gid, self.trigger_group_index)]:
            self.process_status_dict[(self.gid, self.trigger_group_index)].remove(self.trigger_word)