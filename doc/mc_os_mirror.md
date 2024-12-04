# macos python

## macos iso and dmg list

https://macos.mediy.cn/


```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"


homebrew install
homebrew update


```

- For example, if you use Zsh (the default in newer versions of macOS), open the .zshrc file:

```bash

nano ~/.zshrc
```
- Then add the following line to ensure Homebrew’s Python is used:

```bash

export PATH="/opt/homebrew/bin:$PATH"
```
- Save and close the file, then run:

```bash

source ~/.zshrc
```
- For Bash, update .bash_profile instead:

```bash

nano ~/.bash_profile
```

### venv 

```shell
python3 -m venv myenv

source myenv/bin/activate

pip install -r requirements.txt -i  https://pypi.tuna.tsinghua.edu.cn/simple
```