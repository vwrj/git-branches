from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static, TextLog
from textual import events
import subprocess
from subprocess import Popen, check_output


"""
LEARNINGS:
- key event handlers need to be defined on the top-level App, not on child widgets.
"""

class Branches(Container):
    """Displays a list of most recent git branches"""

    BRANCHES = []
    INDEX = 0

    def fetch_recent_git_branches(self, n: int):
        command = "git branch --sort=-committerdate"
        gb = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE)
        out = check_output(('head', f'-{n}'), stdin=gb.stdout).decode('utf-8')
        gb.wait()
        raw = out.split('\n')
        for a in raw:
            b = a.strip()
            if b:
                self.BRANCHES.append(b.replace('* ', ''))

    def compose(self) -> ComposeResult:
        self.fetch_recent_git_branches(10) 
        for (i, b) in enumerate(self.BRANCHES):
            branch = Static(b, id=f"c-{i}")
            branch.add_class("list_item")
            if i == self.INDEX:
                branch.add_class("selected")
            yield branch


class GitBranchApp(App):
    """A Textual app to view recent git branches and choose one to check out"""

    CSS_PATH = "gitbranch.css"

    def compose(self) -> ComposeResult:
        """Create child widgets for the App"""
        yield Header()
        yield Footer()
        yield Branches(id="b")

    def key_j(self) -> None:
        branch_list = self.query_one("#b")
        i = branch_list.INDEX
        length = len(branch_list.BRANCHES)

        self.query_one(f"#c-{i}").remove_class("selected")
        branch_list.INDEX = (i + 1) % length
        self.query_one(f"#c-{branch_list.INDEX}").add_class("selected")

    def key_k(self) -> None:
        branch_list = self.query_one("#b")
        i = branch_list.INDEX
        length = len(branch_list.BRANCHES)

        self.query_one(f"#c-{i}").remove_class("selected")
        branch_list.INDEX = (i + length - 1) % length
        self.query_one(f"#c-{branch_list.INDEX}").add_class("selected")

    def key_enter(self) -> None:
        branch_list = self.query_one("#b")
        item = self.query_one(f"#c-{branch_list.INDEX}")
        out = check_output(('git', 'checkout', str(item.renderable))).decode('utf-8')
        self.exit()


if __name__ == "__main__":
    app = GitBranchApp()
    app.run()
