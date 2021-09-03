# -*- coding: utf-8 -*-

"""Boilerplate:
A one line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

<div id = "contributors">
Created on Wed Aug 25 10:40:20 2021
@author: Timothe
</div>
"""

import os, sys
from warnings import warn
import ast

import pathes
import strings

_EXCLUDE_BALISES = {"exclude_module":"EXCLUDE_MODULE_FROM_MKDOCSTRINGS","exclude_func_class":"EXCLUDE_FUNC_OR_CLASS_FROM_MKDOCSTRINGS"}

class mkds_pyfile_parser(ast.NodeVisitor):
    """
    Attributes:
        modulename str:
            the name of the module without the .py extension
        content dict:
            a dictionnary with two keys : `functions` and `classes`,
            each of wich containing a list of the classes and functions in the module
            with the format : "module.fooclass" or "module.foofunction".
            ``content`` doesn't registers classes internal functions.
    """
    def __init__(self, path):
        """
        Constructor method of the class.

        Args:
            path (str): The full path to a python file that has been parsed.

        Returns:
            mkds_pyfile_parser : An instance of this class.

        """
        # track context name and set of names marked as `global`
        self.path = path
        self.modulename = os.path.splitext(os.path.split(self.path)[1])[0]
        self.context = [self.modulename]
        self.content = {"functions":[],"classes":[]}

    def is_empty(self):
        """


        Returns:
            bool: DESCRIPTION.

        """
        if len(self.content["functions"]) == 0 and len(self.content["classes"]) == 0 :
            return True
        return False

    def check_exclusion(self,node,exclusion_context):
        node_doctring = ast.get_docstring(node)
        if node_doctring is not None and "<" + _EXCLUDE_BALISES[exclusion_context] + ">" in node_doctring :
            # hashtags are added around the balise to make this able to see this file even thou it contains the balise in it's text.
            # Note : not usefull anymore as we check only the presence of the balises inside doctrings and not inside code.
            # Let's keept this feature anyway to prevent any unexpected behavior trouble.
            return True
        return False

    def aggreg_context(self):
        aggregator = []
        for item in self.context:
            aggregator.append(item)
            aggregator.append(".")
        aggregator.pop()
        agg = ''.join(aggregator)
        return agg

    def visit_FunctionDef(self, node):
        self.context.append(node.name)
        if len(self.context) == 2 and not self.check_exclusion(node,"exclude_func_class"):
            #len(context) == 2 when we are inside module, and function. If we are inside module, class, function , we are == 3. And we don't want to register class functions.
            self.content["functions"].append(self.aggreg_context())
        self.generic_visit(node)
        self.context.pop()

    # treat coroutines the same way
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.context.append(node.name)
        if not self.check_exclusion(node,"exclude_func_class"):
            self.content["classes"].append(self.aggreg_context())
        self.generic_visit(node)
        self.context.pop()

    def visit_Lambda(self, node):
        # lambdas are just functions, albeit with no statements, so no assignments.
        # As they have no name though, they won't be documented
        self.generic_visit(node)

    def visit_Module(self, node):
        if self.check_exclusion(node,"exclude_module"):
            return None
        self.generic_visit(node)

    def visit(self,generic_arg=None):
        """
        Takes as argument the output of ast.parse().
        Itself takes as argument the str returned by reading a whole ``.py`` file.
        This method is the way we visit every node of the file and on the way,
        we register the classes and functions names.

        Returns:
            NoneType : Returns None. Use to be able to fill ``content`` with the classes and methods of the file.

        Example:
            ```python
            parser = mkds_pyfile_parser(filepath)
            parser.visit()
            print(parser.content)
            ```
        Tip:
            To explude functions/classes from being returned and lead to the creation of a mkdoctrings entry, use the balise :
            ``EXCLUDE_FUNC_OR_CLASS_FROM_MKDOCSTRINGS`` anywhere in the doctring of your function/class.
            In the same way, a whole module can be excluded by including the balise
            <``EXCLUDE_MODULE_FROM_MKDOCSTRINGS``> (with angle brackets) anywhere in the boilerplate at the top of your module.
        """
        if generic_arg is None :
            #This case is entered when a user externally calls visit with no argument.
            with open(self.path,"r") as pyf:
                parsed_data = ast.parse(pyf.read())
            return super().visit(parsed_data)
        else :
            #This case is required when visit is called internally, by the super class ast.NodeVisitor.generic_visit(), with one argument.
            #In that case, we just call the parent implementation of visit and return it's result transparently to not affect the class's behaviour.
            return super().visit(generic_arg)


class mkds_markdown_indexfile():
    """TODO : make this class so we can add modules, their top doctring and their
    child classes and function as list in a summary inside index.md in the doc folder or any project.

    Also : add balises <div id = "contributors"> </div> around the boilerplate
    'Created on Wed Aug 25 10:40:20 2021 @author: Timothe' to avoid putting it everywhere in the doc.

    Add a balise to skip a part of the doctring <div id = "exclude_part_from_mkds"> </div>
    Add a balise to skip the entire doctring <div id = "exclude_boilerplate_from_mkds">
    Add a balise to specify the position of the content_index. <div id = "content_index">

    Add links between summary items and their .md pages
    """
    def __init__(self,path):
        pass



def mkds_mod_mkdocs_yml_archi(path : str,appendings : list) -> None:
    filepath = os.path.join(path,"mkdocs.yml")
    original_content = []

    with open(filepath,"r") as f :
        for line in f.readlines():
            original_content.append(line)
            if "index.md" in line :
                break
    with open(filepath,"w") as f :
        for line in original_content :
            f.write(line)
        for line in appendings :
            f.write(line)

def mkds_markdownfile_content(item_name : str,item_type : str) -> str:
    content = []
    content.append("# \n")
    content.append("::: ")
    content.append(item_name + "\n")

    if item_type == "functions" :
        content.append("""    handler: python
    rendering:
      show_root_heading: true
      show_root_full_path : false
      show_category_heading : false
      heading_level : 1""")

    if item_type == "classes" :
        content.append("""    handler: python
    rendering:
      show_root_heading: true
      show_root_full_path : false
      show_category_heading : true
      show_root_members_full_path : true
      show_if_no_docstring : false
      heading_level : 1""")

    return ''.join(content)

def mkds_make_docfiles(path : str) -> None:

    def _entry_level(level : int,entry_name : str,quotes : bool = False) -> str :
        line =  "    "*level + "- "
        if quotes :
            entry_name = _quoting(entry_name)
        return line + entry_name + ": "

    def _quoting(name : str) -> str:
        return "'" + name + "'"

    def _eol() -> str:
        return "\n"

    def _rel_path_md(names : str) -> str:
        rel_path = ""
        for name in names :
            rel_path = rel_path + name + "\\"
        rel_path = rel_path[:-1]
        return _quoting(rel_path + ".md")

    docpath = os.path.join(path,"doc")
    pathes.is_or_makedir(docpath)
    matched_py_files = pathes.re_folder_search(path,r".\.py$")
    yml_new_architecture = []

    for filepath in matched_py_files :

        parser = mkds_pyfile_parser(filepath)
        parser.visit()

        if not parser.is_empty():

            module_docpath = os.path.join(docpath,parser.modulename)
            pathes.is_or_makedir(module_docpath)
            matched_md_files = pathes.re_folder_search(module_docpath,r".\.md$")
            if matched_md_files is not None :
                for md_file_path in matched_md_files:
                    os.remove(md_file_path)
            yml_new_architecture.append(_entry_level(1,parser.modulename)+_eol())

            for func_type in ["classes","functions"]:

                for func_item in parser.content[func_type]:

                    func_name = func_item.split(".")[1]
                    module_docfilename = os.path.join(module_docpath,func_name+".md")

                    yml_new_architecture.append(_entry_level(2,func_name,True)+_rel_path_md([parser.modulename,func_name])+_eol())

                    if os.path.isfile(module_docfilename):
                        warn("Warning : doc file have been overwritten")

                    with open(module_docfilename, "w") as mof :
                        mof.write(mkds_markdownfile_content(func_item,func_type))

    mkds_mod_mkdocs_yml_archi(path,yml_new_architecture)


if __name__ == "__main__" :

    test_path = r"C:\Users\Timothe\NasgoyaveOC\Professionnel\TheseUNIC\DevScripts\Python\__packages__\pGenUtils"

    mkds_make_docfiles(test_path)