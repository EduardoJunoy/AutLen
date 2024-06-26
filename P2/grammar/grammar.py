from __future__ import annotations

from collections import deque
from typing import AbstractSet, Collection, MutableSet, Optional, Dict, List, Optional

class RepeatedCellError(Exception):
    """Exception for repeated cells in LL(1) tables."""

class SyntaxError(Exception):
    """Exception for parsing errors."""

class Grammar:
    """
    Class that represents a grammar.

    Args:
        terminals: Terminal symbols of the grammar.
        non_terminals: Non terminal symbols of the grammar.
        productions: Dictionary with the production rules for each non terminal
          symbol of the grammar.
        axiom: Axiom of the grammar.

    """
    def __init__(
        self,
        terminals: AbstractSet[str],
        non_terminals: AbstractSet[str],
        productions: Dict[str, List[str]],
        axiom: str,
    ) -> None:
        if terminals & non_terminals:
            raise ValueError(
                "Intersection between terminals and non terminals "
                "must be empty.",
            )

        if axiom not in non_terminals:
            raise ValueError(
                "Axiom must be included in the set of non terminals.",
            )

        if non_terminals != set(productions.keys()):
            raise ValueError(
                f"Set of non-terminals and productions keys should be equal."
            )
        
        for nt, rhs in productions.items():
            if not rhs:
                raise ValueError(
                    f"No production rules for non terminal symbol {nt} "
                )
            for r in rhs:
                for s in r:
                    if (
                        s not in non_terminals
                        and s not in terminals
                    ):
                        raise ValueError(
                            f"Invalid symbol {s}.",
                        )

        self.terminals = terminals
        self.non_terminals = non_terminals
        self.productions = productions
        self.axiom = axiom

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"terminals={self.terminals!r}, "
            f"non_terminals={self.non_terminals!r}, "
            f"axiom={self.axiom!r}, "
            f"productions={self.productions!r})"
        )


    def compute_first(self, sentence: str) -> AbstractSet[str]:
        """
        Method to compute the first set of a string.

        Args:
            str: string whose first set is to be computed.

        Returns:
            First set of str.
        """

	# TO-DO: Complete this method for exercise 3...
        for s in sentence:
            if (s not in self.terminals) and (s not in self.non_terminals):
                raise ValueError
        return self.compute_first_aux(sentence, set())
    

    def compute_first_aux(self, sentence: str, visitados: set[str]) -> AbstractSet[str]:
        computefirst:set[str] = set() 
        if (sentence == "") or (sentence is None): 
            computefirst.add("")
            return computefirst
        for symbol in sentence: 
            if symbol in self.terminals: 
                computefirst.add(symbol)
                return computefirst
            else:
                for key,value in self.productions.items(): 
                    if key==symbol:
                        for v in value:
                            visitados.add(v)
                            computefirst.update(self.compute_first_aux(v, visitados)) 
                if "" not in computefirst: 
                    return computefirst
                else:
                    computefirst.remove("")

        computefirst.add("") 
        return computefirst
    
    def compute_follow(self, symbol: str) -> AbstractSet[str]:
        """
        Method to compute the follow set of a non-terminal symbol.

        Args:
            symbol: non-terminal whose follow set is to be computed.

        Returns:
            Follow set of symbol.
        """

	# TO-DO: Complete this method for exercise 4...
        dic={}

        for key in self.non_terminals:
            if key == self.axiom :
                dic[key]=['$']
            else:
                dic[key]=[]
        dic_aux=dic
        dic_aux={}
        flag=1
        while flag==1:
            for k in self.non_terminals:
                for key, value in self.productions.items():
                    for v in value:
                        if k in v:
                            if k==v[-1]:
                                dic[k]+= dic[key]
                            else:
                                i=v.find(k)
                                letra=v[i+1]
                                if letra in self.non_terminals:
                                    flag2=1
                                    while flag2==1:        
                                        c=self.compute_first_aux(letra,set())
                                        for p in c:
                                            if '' == p:
                                                if letra==v[-1]:
                                                    dic[k]+=dic[key]
                                                    flag2=0
                                                else:
                                                    i=i+1
                                                    letra==v[i+1]
                                            dic[k]+=p
                                else: 
                                    dic[k]+=letra
                                    

            #print("NUMVECES")
            #print(dic)
            if dic_aux == dic :
                flag=0
            else:
                dic_aux=dic

        for d in dic:
            variable=set(dic[d])
            variable_aux=list(variable)
            dic[d]=variable_aux
        #print(dic)
        result=list()
        for clave, valor in dic.items():
            if clave==symbol:
                result=valor
        return set(result)

    def get_ll1_table(self) -> Optional[LL1Table]:
        """
        Method to compute the LL(1) table.

        Returns:
            LL(1) table for the grammar, or None if the grammar is not LL(1).
        """

	# TO-DO: Complete this method for exercise 5...
        table = LL1Table(self.non_terminals, self.terminals)
        for key, value in self.productions.items():
            for v in value:
                c=self.compute_first_aux(v,set())
                for p in c:
                    if p != '':
                        table.add_cell(key,p,v)
                if '' in c:
                    s=self.compute_follow(v)
                    for n in s:
                        for clave, valor in table.cells.items():
                            for cl2,va2 in valor.items():
                                if cl2==n and va2 !=None:
                                    return None
                                else:
                                    table.add_cell(key,n,v)
        return table


    def is_ll1(self) -> bool:
        return self.get_ll1_table() is not None


class LL1Table:
    """
    LL1 table. Initially all cells are set to None (empty). Table cells
    must be filled by calling the method add_cell.

    Args:
        non_terminals: Set of non terminal symbols.
        terminals: Set of terminal symbols.

    """

    def __init__(
        self,
        non_terminals: AbstractSet[str],
        terminals: AbstractSet[str],
    ) -> None:

        if terminals & non_terminals:
            raise ValueError(
                "Intersection between terminals and non terminals "
                "must be empty.",
            )

        self.terminals: AbstractSet[str] = terminals
        self.non_terminals: AbstractSet[str] = non_terminals
        self.cells: Dict[str, Dict[str, Optional[str]]] = {nt: {t: None for t in terminals} for nt in non_terminals}

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"terminals={self.terminals!r}, "
            f"non_terminals={self.non_terminals!r}, "
            f"cells={self.cells!r})"
        )

    def add_cell(self, non_terminal: str, terminal: str, cell_body: str) -> None:
        """
        Adds a cell to an LL(1) table.

        Args:
            non_terminal: Non termial symbol (row)
            terminal: Terminal symbol (column)
            cell_body: content of the cell 

        Raises:
            RepeatedCellError: if trying to add a cell already filled.
        """
        if non_terminal not in self.non_terminals:
            raise ValueError(
                "Trying to add cell for non terminal symbol not included "
                "in table.",
            )
        if terminal not in self.terminals:
            raise ValueError(
                "Trying to add cell for terminal symbol not included "
                "in table.",
            )
        if not all(x in self.terminals | self.non_terminals for x in cell_body):
            raise ValueError(
                "Trying to add cell whose body contains elements that are "
                "not either terminals nor non terminals.",
            )            
        if self.cells[non_terminal][terminal] is not None:
            raise RepeatedCellError(
                f"Repeated cell ({non_terminal}, {terminal}).")
        else:
            self.cells[non_terminal][terminal] = cell_body

    def analyze(self, input_string: str, start: str) -> ParseTree:
        """
        Method to analyze a string using the LL(1) table.

        Args:
            input_string: string to analyze.
            start: initial symbol.

        Returns:
            ParseTree object with either the parse tree (if the elective exercise is solved)
            or an empty tree (if the elective exercise is not considered).

        Raises:
            SyntaxError: if the input string is not syntactically correct.
        """

	# TO-DO: Complete this method for exercise 2...
        pila = [('$',-1), (start, 0)]
        orden = 0
        tree = ParseTree(root = start)
        tree_l = [tree]
        while (len(pila) > 0) and (orden < len(input_string)):
            e, pos = pila.pop()
            if (e in self.terminals) or (e == "$"):
                if e == input_string[orden]:
                    orden += 1
                else:
                    raise SyntaxError
                    
            elif e in self.non_terminals:
                casilla = e
                if casilla in self.cells:
                    children = []
                    a=""
                    for clave, value in self.cells[e].items():
                        if (value != None) and (value != "") and (input_string[orden]==clave) :
                            a=(str(value))
                    if not a :
                        node = ParseTree(root ='λ')
                        children.append(node)
                    else:
                        for j in a[::-1] :
                            node = ParseTree(root = j)
                            length = len(tree_l)
                            tree_l.append(node)
                            pila += [(j, length)]
                            children.append(node)
                    children.reverse()
                    tree_l[pos].add_children(children)
                else:
                    raise SyntaxError 
            else:
                raise SyntaxError

        if orden < len(input_string) or len(pila) > 0:
            raise SyntaxError
        return tree
    
    
class ParseTree():
    """
    Parse Tree.

    Args:
        root: root node of the tree.
        children: list of children, which are also ParseTree objects.
    """
    def __init__(self, root: str, children: Collection[ParseTree] = []) -> None:
        self.root = root
        self.children = children

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.root!r}: {self.children})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
            self.root == other.root
            and len(self.children) == len(other.children)
            and all([x.__eq__(y) for x, y in zip(self.children, other.children)])
        )

    def add_children(self, children: Collection[ParseTree]) -> None:
        self.children = children
