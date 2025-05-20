_artifact_list = []
_selected_artifact = None

def set_artifact_list(artifact_list):
    global _artifact_list
    _artifact_list = artifact_list


def get_artifact_list():
    return _artifact_list

def set_selected_artifact(artifact):
    global _selected_artifact
    _selected_artifact = artifact

def get_selected_artifact():
    return _selected_artifact
