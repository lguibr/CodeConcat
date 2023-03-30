# CodeConcat

CodeConcat is a simple command-line interface (CLI) tool that enables developers to quickly and easily concatenate an entire codebase from a GitHub repository into a single text file. This bundled file includes a directory tree, file paths, and file content, making it an excellent resource for code review, documentation, or sharing with others. CodeConcat supports specifying a particular branch of the repository and generates the output file in a human-readable format.

## Features

Retrieve code from any GitHub repository (public or private)
Specify a particular branch of the repository (optional)
Generate a directory tree for the entire codebase
Include file paths and file content in the output
Produce a human-readable text file
Customize the output file path and name
Installation
Before using CodeConcat, make sure you have Python installed on your system. You can download Python from the official website: https://www.python.org/downloads/

To install CodeConcat, simply clone the repository:

```bash

git clone https://github.com/your-username/CodeConcat.git
cd CodeConcat
```

## Usage

To use CodeConcat, run the following command with the required arguments:

```bash

python main.py github-username/repository?/optional-branch ./preffix/path/to.txt ./suffix.txt ./output/path/to.txt
```

## Arguments

- github-username/repository?/optional-branch: The GitHub repository's URL in the format username/repository/branch. Replace username with the GitHub user's name, repository with the repository's name, and branch with the specific branch you want to target (optional).
- ./preffix/path/to.txt: The path to the text file containing the prefix that will be added to the output file.
- ./suffix.txt: The path to the text file containing the suffix that will be added to the output file.
- ./output/path/to.txt: The path to the output file where the concatenated codebase will be saved.

## Example

Suppose you want to concatenate the codebase from the sample-user/sample-repo repository and save it in a file called sample-output.txt in the current directory. The command would look like this:

```bash
python main.py sample-user/sample-repo ./prefix.txt ./suffix.txt ./sample-output.txt
```

## Contributing

We welcome contributions to CodeConcat! If you have any ideas, suggestions, or bug reports, please feel free to open an issue or submit a pull request.

## License

CodeConcat is released under the MIT License.
