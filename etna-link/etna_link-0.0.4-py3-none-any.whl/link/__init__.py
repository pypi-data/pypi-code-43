#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import clang.cindex
import enum
from typing import Iterator, List, Tuple

"""
Thin wrapper around clang cindex AST manipulation library

It allows traversing the AST and calling user-provided callbacks for the requested node types
"""


class TranslationUnitLoadError(Exception):
    """
    Class representing an error when attempting to load a translation unit
    """
    pass


class ParseError(Exception):
    """
    Class representing a parse error when inspecting clang tokens
    """
    pass


NodeKind = enum.Enum('NodeKind',
                     'TRANSLATION_UNIT '
                     'FUNCTION_DECL '
                     'FUNCTION_DEFINITION '
                     'DECL_STATEMENT '
                     'VAR_DECL '
                     'VARIABLE_DEFINITION '
                     'STRUCT_DECL '
                     'STRUCT_DEFINITION '
                     'UNION_DECL '
                     'UNION_DEFINITION '
                     'ENUM_DECL '
                     'ENUM_DEFINITION '
                     'FIELD_DECL '
                     'TYPEDEF_DECL '
                     'TYPE_REF '
                     'MACRO_DEFINITION '
                     'ENUM_CONSTANT_DECL '
                     'GOTO_STATEMENT '
                     'INDIRECT_GOTO_STATEMENT '
                     'LABEL_REF '
                     'LABEL_STATEMENT '
                     'ADDR_LABEL_EXPR '
                     'COMPOUND_STATEMENT '
                     'PARAM_DECL '
                     'RETURN_STATEMENT '
                     'BINARY_OPERATOR '
                     'COMPOUND_ASSIGNMENT_OPERATOR '
                     'COMPOUND_LITERAL_EXPR '
                     'INIT_LIST_EXPR '
                     'PAREN_EXPR '
                     'MEMBER_REF_EXPR '
                     'INTEGER_LITERAL '
                     'CHARACTER_LITERAL '
                     'STRING_LITERAL '
                     'FLOATING_LITERAL '
                     'CALL_EXPR '
                     'C_CAST_EXPR '
                     'DECL_REF_EXPR '
                     'UNARY_EXPR '
                     'UNARY_OPERATOR '
                     'ARRAY_SUBSCRIPT_EXPR '
                     'TERNARY_OPERATOR '
                     'IF_STATEMENT '
                     'WHILE_STATEMENT '
                     'DO_STATEMENT '
                     'FOR_STATEMENT '
                     'SWITCH_STATEMENT '
                     'CASE_STATEMENT '
                     'DEFAULT_STATEMENT '
                     'BREAK_STATEMENT '
                     'CONTINUE_STATEMENT '
                     'NULL_STATEMENT '
                     'UNEXPOSED_EXPR '
                     'UNEXPOSED_STMT '
                     'UNEXPOSED_ATTR '
                     'UNEXPOSED_DECL '
                     'STATEMENT_EXPR '
                     'ASM_STATEMENT '
                     'MACRO_INSTANTIATION '
                     'IGNORED '
                     )


def _identify_node_kind(node) -> NodeKind:
    """
    Identify the kind of a raw cindex node

    :param node:        the node

    :return:            the corresponding kind
    """
    translation = {
        clang.cindex.CursorKind.TRANSLATION_UNIT: NodeKind.TRANSLATION_UNIT,
        clang.cindex.CursorKind.FUNCTION_DECL: NodeKind.FUNCTION_DECL,
        clang.cindex.CursorKind.DECL_STMT: NodeKind.DECL_STATEMENT,
        clang.cindex.CursorKind.VAR_DECL: NodeKind.VAR_DECL,
        clang.cindex.CursorKind.TYPEDEF_DECL: NodeKind.TYPEDEF_DECL,
        clang.cindex.CursorKind.TYPE_REF: NodeKind.TYPE_REF,
        clang.cindex.CursorKind.STRUCT_DECL: NodeKind.STRUCT_DECL,
        clang.cindex.CursorKind.UNION_DECL: NodeKind.UNION_DECL,
        clang.cindex.CursorKind.ENUM_DECL: NodeKind.ENUM_DECL,
        clang.cindex.CursorKind.FIELD_DECL: NodeKind.FIELD_DECL,
        clang.cindex.CursorKind.MACRO_DEFINITION: NodeKind.MACRO_DEFINITION,
        clang.cindex.CursorKind.ENUM_CONSTANT_DECL: NodeKind.ENUM_CONSTANT_DECL,
        clang.cindex.CursorKind.GOTO_STMT: NodeKind.GOTO_STATEMENT,
        clang.cindex.CursorKind.INDIRECT_GOTO_STMT: NodeKind.INDIRECT_GOTO_STATEMENT,
        clang.cindex.CursorKind.LABEL_REF: NodeKind.LABEL_REF,
        clang.cindex.CursorKind.LABEL_STMT: NodeKind.LABEL_STATEMENT,
        clang.cindex.CursorKind.ADDR_LABEL_EXPR: NodeKind.ADDR_LABEL_EXPR,
        clang.cindex.CursorKind.PARM_DECL: NodeKind.PARAM_DECL,
        clang.cindex.CursorKind.COMPOUND_STMT: NodeKind.COMPOUND_STATEMENT,
        clang.cindex.CursorKind.RETURN_STMT: NodeKind.RETURN_STATEMENT,
        clang.cindex.CursorKind.BINARY_OPERATOR: NodeKind.BINARY_OPERATOR,
        clang.cindex.CursorKind.COMPOUND_ASSIGNMENT_OPERATOR: NodeKind.COMPOUND_ASSIGNMENT_OPERATOR,
        clang.cindex.CursorKind.COMPOUND_LITERAL_EXPR: NodeKind.COMPOUND_LITERAL_EXPR,
        clang.cindex.CursorKind.INIT_LIST_EXPR: NodeKind.INIT_LIST_EXPR,
        clang.cindex.CursorKind.PAREN_EXPR: NodeKind.PAREN_EXPR,
        clang.cindex.CursorKind.MEMBER_REF_EXPR: NodeKind.MEMBER_REF_EXPR,
        clang.cindex.CursorKind.INTEGER_LITERAL: NodeKind.INTEGER_LITERAL,
        clang.cindex.CursorKind.CHARACTER_LITERAL: NodeKind.CHARACTER_LITERAL,
        clang.cindex.CursorKind.STRING_LITERAL: NodeKind.STRING_LITERAL,
        clang.cindex.CursorKind.FLOATING_LITERAL: NodeKind.FLOATING_LITERAL,
        clang.cindex.CursorKind.CALL_EXPR: NodeKind.CALL_EXPR,
        clang.cindex.CursorKind.CSTYLE_CAST_EXPR: NodeKind.C_CAST_EXPR,
        clang.cindex.CursorKind.DECL_REF_EXPR: NodeKind.DECL_REF_EXPR,
        clang.cindex.CursorKind.CXX_UNARY_EXPR: NodeKind.UNARY_EXPR,
        clang.cindex.CursorKind.UNARY_OPERATOR: NodeKind.UNARY_OPERATOR,
        clang.cindex.CursorKind.ARRAY_SUBSCRIPT_EXPR: NodeKind.ARRAY_SUBSCRIPT_EXPR,
        clang.cindex.CursorKind.CONDITIONAL_OPERATOR: NodeKind.TERNARY_OPERATOR,
        clang.cindex.CursorKind.IF_STMT: NodeKind.IF_STATEMENT,
        clang.cindex.CursorKind.WHILE_STMT: NodeKind.WHILE_STATEMENT,
        clang.cindex.CursorKind.DO_STMT: NodeKind.DO_STATEMENT,
        clang.cindex.CursorKind.FOR_STMT: NodeKind.FOR_STATEMENT,
        clang.cindex.CursorKind.SWITCH_STMT: NodeKind.SWITCH_STATEMENT,
        clang.cindex.CursorKind.CASE_STMT: NodeKind.CASE_STATEMENT,
        clang.cindex.CursorKind.DEFAULT_STMT: NodeKind.DEFAULT_STATEMENT,
        clang.cindex.CursorKind.BREAK_STMT: NodeKind.BREAK_STATEMENT,
        clang.cindex.CursorKind.CONTINUE_STMT: NodeKind.CONTINUE_STATEMENT,
        clang.cindex.CursorKind.NULL_STMT: NodeKind.NULL_STATEMENT,
        clang.cindex.CursorKind.UNEXPOSED_EXPR: NodeKind.UNEXPOSED_EXPR,
        clang.cindex.CursorKind.UNEXPOSED_STMT: NodeKind.UNEXPOSED_STMT,
        clang.cindex.CursorKind.UNEXPOSED_ATTR: NodeKind.UNEXPOSED_ATTR,
        clang.cindex.CursorKind.UNEXPOSED_DECL: NodeKind.UNEXPOSED_DECL,
        clang.cindex.CursorKind.StmtExpr: NodeKind.STATEMENT_EXPR,
        clang.cindex.CursorKind.ASM_STMT: NodeKind.ASM_STATEMENT,
        clang.cindex.CursorKind.MACRO_INSTANTIATION: NodeKind.MACRO_INSTANTIATION,
    }
    additional_def_kinds = {
        NodeKind.FUNCTION_DECL: NodeKind.FUNCTION_DEFINITION,
        NodeKind.VAR_DECL: NodeKind.VARIABLE_DEFINITION,
        NodeKind.STRUCT_DECL: NodeKind.STRUCT_DEFINITION,
        NodeKind.UNION_DECL: NodeKind.UNION_DEFINITION,
        NodeKind.ENUM_DECL: NodeKind.ENUM_DEFINITION,
    }
    if node.kind not in translation:
        return NodeKind.IGNORED
    val = translation[node.kind]
    if node.is_definition() and val in additional_def_kinds:
        return additional_def_kinds[val]
    return val


def _create_node_info(node_kind, node, tu):
    """
    Create a more strongly-typed wrapper object around a raw cindex node

    :param node_kind:       a kind as returned by _identify_node_kind
    :param node:            a raw cindex node
    :param tu:              the translation unit containing the node

    :return:                the appropriate node wrapper
    """
    node_types = {
        NodeKind.TRANSLATION_UNIT: TranslationUnit,
        NodeKind.FUNCTION_DECL: FunctionDecl,
        NodeKind.FUNCTION_DEFINITION: FunctionDef,
        NodeKind.VAR_DECL: VariableDecl,
        NodeKind.VARIABLE_DEFINITION: VariableDef,
        NodeKind.DECL_STATEMENT: DeclStatement,
        NodeKind.TYPEDEF_DECL: Typedef,
        NodeKind.TYPE_REF: TypeRef,
        NodeKind.STRUCT_DECL: StructDecl,
        NodeKind.STRUCT_DEFINITION: StructDef,
        NodeKind.UNION_DECL: UnionDecl,
        NodeKind.UNION_DEFINITION: UnionDef,
        NodeKind.ENUM_DECL: EnumDecl,
        NodeKind.ENUM_DEFINITION: EnumDef,
        NodeKind.FIELD_DECL: FieldDecl,
        NodeKind.MACRO_DEFINITION: MacroDef,
        NodeKind.ENUM_CONSTANT_DECL: EnumConstant,
        NodeKind.GOTO_STATEMENT: GotoStatement,
        NodeKind.INDIRECT_GOTO_STATEMENT: IndirectGotoStatement,
        NodeKind.LABEL_REF: LabelRef,
        NodeKind.LABEL_STATEMENT: LabelStatement,
        NodeKind.ADDR_LABEL_EXPR: AddrLabelExpr,
        NodeKind.PARAM_DECL: ParamDecl,
        NodeKind.COMPOUND_STATEMENT: CompoundStatement,
        NodeKind.RETURN_STATEMENT: ReturnStatement,
        NodeKind.BINARY_OPERATOR: BinaryOperator,
        NodeKind.COMPOUND_ASSIGNMENT_OPERATOR: CompoundAssignmentOperator,
        NodeKind.COMPOUND_LITERAL_EXPR: CompoundLiteralExpr,
        NodeKind.INIT_LIST_EXPR: InitListExpr,
        NodeKind.PAREN_EXPR: ParenExpr,
        NodeKind.MEMBER_REF_EXPR: MemberRef,
        NodeKind.INTEGER_LITERAL: IntegerLiteral,
        NodeKind.CHARACTER_LITERAL: CharacterLiteral,
        NodeKind.STRING_LITERAL: StringLiteral,
        NodeKind.FLOATING_LITERAL: FloatingLiteral,
        NodeKind.CALL_EXPR: CallExpr,
        NodeKind.C_CAST_EXPR: CCastExpr,
        NodeKind.DECL_REF_EXPR: DeclRefExpr,
        NodeKind.UNARY_EXPR: UnaryExpr,
        NodeKind.UNARY_OPERATOR: UnaryOperator,
        NodeKind.ARRAY_SUBSCRIPT_EXPR: ArraySubscriptExpr,
        NodeKind.TERNARY_OPERATOR: TernaryOperator,
        NodeKind.IF_STATEMENT: IfStatement,
        NodeKind.WHILE_STATEMENT: WhileStatement,
        NodeKind.DO_STATEMENT: DoStatement,
        NodeKind.FOR_STATEMENT: ForStatement,
        NodeKind.SWITCH_STATEMENT: SwitchStatement,
        NodeKind.CASE_STATEMENT: CaseStatement,
        NodeKind.DEFAULT_STATEMENT: DefaultStatement,
        NodeKind.BREAK_STATEMENT: BreakStatement,
        NodeKind.CONTINUE_STATEMENT: ContinueStatement,
        NodeKind.NULL_STATEMENT: NullStatement,
        NodeKind.UNEXPOSED_EXPR: UnexposedExpr,
        NodeKind.UNEXPOSED_STMT: UnexposedStmt,
        NodeKind.UNEXPOSED_ATTR: UnexposedAttr,
        NodeKind.UNEXPOSED_DECL: UnexposedDecl,
        NodeKind.STATEMENT_EXPR: StatementExpr,
        NodeKind.ASM_STATEMENT: AsmStatement,
        NodeKind.MACRO_INSTANTIATION: MacroInstantiation,
        NodeKind.IGNORED: Ignored,
    }
    return node_types[node_kind](node_kind, node, tu)


def _wrap_node(node: clang.cindex.Cursor, tu: clang.cindex.TranslationUnit):
    """
    Wrap a raw cindex node inside a wrapper object

    :param node:        the node to wrap
    :param tu:          the translation unit containing the node

    :return:            the wrapped node
    """
    node_kind = _identify_node_kind(node)
    node_info = _create_node_info(node_kind, node, tu)
    return node_info


class SourceLocation:
    """
    Class representing a location in the source code
    """

    def __init__(self, loc):
        self._loc = loc

    @property
    def file(self):
        return self._loc.file

    @property
    def offset(self):
        return self._loc.offset

    @property
    def line(self):
        return self._loc.line

    @property
    def column(self):
        return self._loc.column

    def __repr__(self):
        return "{{file: {}, line: {}, column: {}, offset: {}}}" \
            .format(self.file, self.line, self.column, self.offset)

    @staticmethod
    def from_position(translation_unit, line, column):
        return SourceLocation(clang.cindex.SourceLocation.from_position(translation_unit.raw_translation_unit,
                                                                        translation_unit.raw_file,
                                                                        line, column))

    @staticmethod
    def from_offset(translation_unit, offset):
        return SourceLocation(clang.cindex.SourceLocation.from_offset(translation_unit.raw_translation_unit,
                                                                      translation_unit.raw_file,
                                                                      offset))

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.file.name == other.file.name and self.offset == other.offset

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(repr(self))


class SourceRange:
    """
    Class representing a range of text in the source code

    The range is half-open, i.e. range.start is included in the range, but range.end is not
    """

    def __init__(self, rng):
        self._rng = rng

    @property
    def start(self) -> SourceLocation:
        return SourceLocation(self._rng.start)

    @property
    def end(self) -> SourceLocation:
        return SourceLocation(self._rng.end)

    def __contains__(self, other: SourceLocation):
        if not isinstance(other, SourceLocation):
            raise RuntimeError("Only a SourceLocation can be in a SourceRange")  # return False
        if other.file is None and self.start.file is None:
            return False
        if self.start.file.name != other.file.name or other.file.name != self.end.file.name:
            return False
        return self.start.offset <= other.offset < self.end.offset

    def __repr__(self):
        return "{{start: {}, end: {}}}".format(self.start, self.end)

    def to_offset_range(self):
        return range(self.start.offset, self.end.offset)

    @staticmethod
    def from_locations(start: SourceLocation, end: SourceLocation):
        return SourceRange(clang.cindex.SourceRange.from_locations(start._loc, end._loc))

    @staticmethod
    def from_line(translation_unit, line):
        return SourceRange.from_locations(SourceLocation.from_position(translation_unit, line, 1),
                                          SourceLocation.from_position(translation_unit, line + 1, 1))


class Token:
    """
    Class to represent a token
    """

    def __init__(self, tok: clang.cindex.Token):
        self._token = tok

    def is_comment(self) -> bool:
        return self._token.kind == clang.cindex.TokenKind.COMMENT

    def is_identifier(self) -> bool:
        return self._token.kind == clang.cindex.TokenKind.IDENTIFIER

    def is_keyword(self) -> bool:
        return self._token.kind == clang.cindex.TokenKind.KEYWORD

    def is_literal(self) -> bool:
        return self._token.kind == clang.cindex.TokenKind.LITERAL

    def is_punctuation(self) -> bool:
        return self._token.kind == clang.cindex.TokenKind.PUNCTUATION

    def text(self) -> str:
        return self._token.spelling

    def location(self) -> SourceLocation:
        return SourceLocation(self._token.location)

    def text_range(self) -> SourceRange:
        return SourceRange(self._token.extent)

    def containing_node(self):
        return _wrap_node(self._token.cursor, self._token.cursor.translation_unit)

    def __repr__(self):
        return "{{value: {}, type: {}}}".format(repr(self.text()), self._token.kind)


TypeKind = enum.Enum('TypeKind',
                     'POINTER '
                     'STRUCT '
                     'UNION '
                     'ENUM '
                     'CONSTANT_SIZED_ARRAY '
                     'INCOMPLETE_ARRAY '
                     'FUNCTION '
                     'TYPEDEF '
                     'COMPLEX '
                     'CHAR_U '
                     'UNSIGNED_CHAR '
                     'UNSIGNED_SHORT '
                     'UNSIGNED_INT '
                     'UNSIGNED_LONG '
                     'UNSIGNED_LONG_LONG '
                     'CHAR_S '
                     'SIGNED_CHAR '
                     'WCHAR '
                     'SHORT '
                     'INT '
                     'LONG '
                     'LONG_LONG '
                     'FLOAT '
                     'DOUBLE '
                     'LONG_DOUBLE '
                     'INVALID '
                     )


def _identify_type_kind(raw_type: clang.cindex.Type) -> Tuple[TypeKind, clang.cindex.Type]:
    """
    Identify the kind of a raw cindex type

    :param raw_type:    the type

    :return:            a tuple containing the corresponding kind, and the type

    Elaborated types are desugared, as they don't carry much meaningful information (at least in C)
    See: https://clang.llvm.org/doxygen/classclang_1_1ElaboratedType.html#details
    """
    translation = {
        clang.cindex.TypeKind.POINTER: TypeKind.POINTER,
        clang.cindex.TypeKind.CONSTANTARRAY: TypeKind.CONSTANT_SIZED_ARRAY,
        clang.cindex.TypeKind.INCOMPLETEARRAY: TypeKind.INCOMPLETE_ARRAY,
        clang.cindex.TypeKind.CHAR_U: TypeKind.CHAR_U,
        clang.cindex.TypeKind.UCHAR: TypeKind.UNSIGNED_CHAR,
        clang.cindex.TypeKind.USHORT: TypeKind.UNSIGNED_SHORT,
        clang.cindex.TypeKind.UINT: TypeKind.UNSIGNED_INT,
        clang.cindex.TypeKind.ULONG: TypeKind.UNSIGNED_LONG,
        clang.cindex.TypeKind.ULONGLONG: TypeKind.UNSIGNED_LONG_LONG,
        clang.cindex.TypeKind.CHAR_S: TypeKind.CHAR_S,
        clang.cindex.TypeKind.SCHAR: TypeKind.SIGNED_CHAR,
        clang.cindex.TypeKind.WCHAR: TypeKind.WCHAR,
        clang.cindex.TypeKind.SHORT: TypeKind.SHORT,
        clang.cindex.TypeKind.INT: TypeKind.INT,
        clang.cindex.TypeKind.LONG: TypeKind.LONG,
        clang.cindex.TypeKind.LONGLONG: TypeKind.LONG_LONG,
        clang.cindex.TypeKind.FLOAT: TypeKind.FLOAT,
        clang.cindex.TypeKind.DOUBLE: TypeKind.DOUBLE,
        clang.cindex.TypeKind.LONGDOUBLE: TypeKind.LONG_DOUBLE,
        clang.cindex.TypeKind.RECORD: TypeKind.STRUCT,
        clang.cindex.TypeKind.TYPEDEF: TypeKind.TYPEDEF,
    }
    if raw_type.kind == clang.cindex.TypeKind.ELABORATED:
        raw_type = raw_type.get_canonical()
    if raw_type.kind not in translation:
        return TypeKind.INVALID, raw_type
    if raw_type.kind == clang.cindex.TypeKind.RECORD:
        # libclang seems to return RECORD for both structures and unions, without a proper way to differentiate them
        if raw_type.get_declaration().kind == clang.cindex.CursorKind.UNION_DECL:
            return TypeKind.UNION, raw_type
    return translation[raw_type.kind], raw_type


def _create_type_info(type_kind: TypeKind, raw_type: clang.cindex.Type):
    """
    Create a more strongly-typed wrapper object around a raw cindex type

    :param type_kind:       a kind as returned by _identify_type_kind
    :param raw_type:        a raw cindex node

    :return:                the appropriate type wrapper
    """
    type_types = {
        TypeKind.POINTER: PointerType,
        TypeKind.CONSTANT_SIZED_ARRAY: ConstantSizedArrayType,
        TypeKind.INCOMPLETE_ARRAY: IncompleteArrayType,
        TypeKind.CHAR_U: IntegralType,
        TypeKind.UNSIGNED_CHAR: IntegralType,
        TypeKind.UNSIGNED_SHORT: IntegralType,
        TypeKind.UNSIGNED_INT: IntegralType,
        TypeKind.UNSIGNED_LONG: IntegralType,
        TypeKind.UNSIGNED_LONG_LONG: IntegralType,
        TypeKind.CHAR_S: IntegralType,
        TypeKind.SIGNED_CHAR: IntegralType,
        TypeKind.WCHAR: IntegralType,
        TypeKind.SHORT: IntegralType,
        TypeKind.INT: IntegralType,
        TypeKind.LONG: IntegralType,
        TypeKind.LONG_LONG: IntegralType,
        TypeKind.FLOAT: FloatingPointType,
        TypeKind.DOUBLE: FloatingPointType,
        TypeKind.LONG_DOUBLE: FloatingPointType,
        TypeKind.STRUCT: StructType,
        TypeKind.UNION: UnionType,
        TypeKind.TYPEDEF: TypedefType,
        TypeKind.INVALID: InvalidType,
    }
    return type_types[type_kind](type_kind, raw_type)


def _wrap_type(raw_type: clang.cindex.Type):
    """
    Wrap a raw cindex type inside a wrapper object

    :param raw_type:    the type to wrap

    :return:            the wrapped type
    """
    type_kind, raw_type = _identify_type_kind(raw_type)
    type_info = _create_type_info(type_kind, raw_type)
    return type_info


class Type:
    """
    Class to represent a type
    """

    def __init__(self, kind: TypeKind, typ: clang.cindex.Type):
        self._kind = kind
        self._typ = typ

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self._typ == other._typ

    def __ne__(self, other):
        return not (self == other)

    def name(self) -> str:
        return self._typ.spelling

    def __repr__(self):
        return self.name()

    def kind(self) -> TypeKind:
        return self._kind

    def size(self) -> int:
        """The size of an object of this type, in bytes"""
        return self._typ.get_size()

    def align(self) -> int:
        """The memory alignment required for an object of this type, in bytes"""
        return self._typ.get_align()

    def is_const_qualified(self) -> bool:
        return self._typ.is_const_qualified()

    def is_volatile_qualified(self) -> bool:
        return self._typ.is_volatile_qualified()

    def is_restrict_qualified(self) -> bool:
        return self._typ.is_restrict_qualified()

    def is_integral(self) -> bool:
        return self.kind() in (
            TypeKind.CHAR_S, TypeKind.SIGNED_CHAR,
            TypeKind.WCHAR, TypeKind.SHORT,
            TypeKind.INT, TypeKind.LONG,
            TypeKind.LONG_LONG,
            TypeKind.CHAR_U,
            TypeKind.UNSIGNED_CHAR,
            TypeKind.UNSIGNED_SHORT,
            TypeKind.UNSIGNED_INT,
            TypeKind.UNSIGNED_LONG,
            TypeKind.UNSIGNED_LONG_LONG,
        )

    def is_floating_point(self) -> bool:
        return self.kind() in (TypeKind.FLOAT, TypeKind.DOUBLE, TypeKind.LONG_DOUBLE)

    def is_pointer(self) -> bool:
        return self.kind() == TypeKind.POINTER

    def is_constant_sized_array(self):
        return self.kind() == TypeKind.CONSTANT_SIZED_ARRAY

    def is_typedef(self) -> bool:
        return self.kind() == TypeKind.TYPEDEF

    def is_struct(self) -> bool:
        return self.kind() == TypeKind.STRUCT

    def is_union(self) -> bool:
        return self.kind() == TypeKind.UNION

    def is_enum(self) -> bool:
        return self.kind() == TypeKind.ENUM

    def is_function(self) -> bool:
        return self._typ.get_result().kind != clang.cindex.TypeKind.INVALID


class IntegralType(Type):
    def is_signed(self):
        """Check whether this integral type is signed or not"""
        return self.kind() in (
            TypeKind.CHAR_S, TypeKind.SIGNED_CHAR,
            TypeKind.WCHAR, TypeKind.SHORT,
            TypeKind.INT, TypeKind.LONG,
            TypeKind.LONG_LONG
        )

    def is_unsigned(self):
        """Check whether this integral type is unsigned or not"""
        return not self.is_signed()


class FloatingPointType(Type):
    pass


class PointerType(Type):
    def pointee_type(self):
        """The type pointed on by this pointer type"""
        return _wrap_type(self._typ.get_pointee())


class FunctionType(Type):
    def return_type(self):
        """The return type for this function type"""
        pass

    def get_parameter_types(self) -> List:
        """Get a list of the types of the parameters for this function type"""
        return list(map(_wrap_type, self._typ.argument_types()))


class ArrayType(Type):
    def element_type(self):
        """The type of the elements in this array type"""
        return _wrap_type(self._typ.get_array_element_type())


class ConstantSizedArrayType(ArrayType):
    def element_count(self) -> int:
        """The number of elements in this array type"""
        return self._typ.get_array_size()


class IncompleteArrayType(ArrayType):
    pass


class RecordType(Type):
    def get_fields_declarations(self) -> Iterator:
        """Get an iterator over all the declarations of the fields in this structure"""
        return map(lambda x: _wrap_node(x, self._typ.translation_unit), self._typ.get_fields())


class StructType(RecordType):
    pass


class UnionType(RecordType):
    pass


class TypedefType(Type):
    def underlying_type(self):
        """The type aliased by this type"""
        return _wrap_type(self._typ.get_canonical())


class InvalidType(Type):
    pass


class ChildrenIterator:
    """
    Wrapper class to allow iterating through children nodes
    """

    def __init__(self, node, tu):
        self._childs = node.get_children()
        self._translation_unit = tu

    def __iter__(self):
        return self

    def __next__(self):
        cur = next(self._childs)
        return _wrap_node(cur, self._translation_unit)


class AbstractNode:
    """
    Base class common to all node classes
    """

    def __init__(self, kind, node, tu):
        self._kind = kind
        self._node = node
        self._translation_unit = tu

    def name(self) -> str:
        return self._node.spelling

    def __repr__(self):
        return self.name()

    def kind(self) -> NodeKind:
        return self._kind

    def location(self) -> SourceLocation:
        return SourceLocation(self._node.location)

    def text_range(self) -> SourceRange:
        return SourceRange(self._node.extent)

    def tokens(self) -> Iterator[Token]:
        return map(Token, clang.cindex.TokenGroup.get_tokens(self._translation_unit, self._node.extent))

    def get_children(self) -> Iterator['AbstractNode']:
        return ChildrenIterator(self._node, self._translation_unit)

    def get_ast_parent(self):
        def _find_parent(parent, node):
            if node == self._node:
                return parent
            for child_node in node.get_children():
                result = _find_parent(node, child_node)
                if result is not None:
                    return result
            return None

        return _wrap_node(_find_parent(None, self._translation_unit.cursor), self._translation_unit)


class CompoundStatement(AbstractNode):
    pass


class ReturnStatement(AbstractNode):
    pass


class StructDecl(AbstractNode):
    def is_definition(self) -> bool:
        return self.kind() == NodeKind.STRUCT_DEFINITION


class StructDef(StructDecl):
    pass


class UnionDecl(AbstractNode):
    def is_definition(self) -> bool:
        return self.kind() == NodeKind.UNION_DEFINITION


class UnionDef(UnionDecl):
    pass


class EnumDecl(AbstractNode):
    def is_definition(self) -> bool:
        return self.kind() == NodeKind.ENUM_DEFINITION


class EnumConstant(AbstractNode):
    def enum_value(self) -> int:
        """The value for this enum constant"""
        return self._node.enum_value


class EnumDef(EnumDecl):
    def underlying_type(self) -> IntegralType:
        """The underlying data type used by this enum type"""
        return _wrap_type(self._node.enum_type)

    def get_enum_constants_declarations(self) -> Iterator[EnumConstant]:
        """Get an iterator over the declarations of this enum's constants"""
        return filter(lambda x: isinstance(x, EnumConstant), self.get_children())


class FieldDecl(AbstractNode):
    def type(self):
        return _wrap_type(self._node.type)


class Typedef(AbstractNode):
    def underlying_type(self):
        """The underlying type aliased by this typedef"""
        return _wrap_type(self._node.underlying_typedef_type)


class TypeRef(AbstractNode):
    def referenced_type(self):
        return _wrap_type(self._node.referenced)


class MemberRef(AbstractNode):
    def member_name(self) -> str:
        return self._node.spelling

    def get_record_type(self):
        return None  # ToDo: find a way to get the corresponding record type


class IntegerLiteral(AbstractNode):
    def get_value(self) -> int:
        toks = self.tokens()
        tok = next(toks)
        v = int(tok.text())
        return v


class CharacterLiteral(AbstractNode):
    def get_value(self) -> str:
        toks = self.tokens()
        tok = next(toks)
        return tok.text()[1:-1]


class StringLiteral(AbstractNode):
    def get_value(self) -> str:
        toks = self.tokens()
        tok = next(toks)
        return tok.text()[1:-1]


class FloatingLiteral(AbstractNode):
    def get_value(self) -> float:
        toks = self.tokens()
        tok = next(toks)
        v = float(tok.text())
        return v


class MacroDef(AbstractNode):
    pass


class LabelStatement(AbstractNode):
    def label_name(self) -> str:
        """The name of the label"""
        return self.name()


class LabelRef(AbstractNode):
    def referenced_label_name(self) -> str:
        """The name of the referenced label"""
        return self.name()


class AddrLabelExpr(AbstractNode):
    pass


class GotoStatement(AbstractNode):
    def target_label_name(self) -> str:
        """The name of the label targeted by this goto"""
        return next(self.get_children())


class IndirectGotoStatement(AbstractNode):
    pass


class CallExpr(AbstractNode):
    def function_name(self) -> str:
        """The name of the function used by this call"""
        return self.name()

    def get_arguments(self) -> Iterator:
        """Get an iterator over the arguments passed by this call"""
        children = self.get_children()
        next(children)
        return children


class TernaryOperator(AbstractNode):
    def left_node(self):
        return next(self._node.get_children())


class BinaryOperator(AbstractNode):
    def __init__(self, kind, node, tu):
        super().__init__(kind, node, tu)
        self._has_operator_info = False
        self._op_sym_rng = None
        self._op_type = None

    def __parse_operator_info(self):
        children = list(self.get_children())
        if len(children) != 2:
            raise RuntimeError("Binary operators should only have two children nodes")
        tokens = self.tokens()
        for pos, tok in enumerate(tokens):
            loc = tok.location()
            if loc not in children[0].text_range() and loc not in children[1].text_range() and loc in self.text_range():
                self._op_sym_rng = tok.text_range()
                self._op_type = tok.text()
        if self._op_type is None:
            raise ParseError("Unable to determine the current operator:", self.text_range())
        self._has_operator_info = True

    def get_operator_symbol_range(self):
        if not self._has_operator_info:
            self.__parse_operator_info()
        return self._op_sym_rng

    def get_operator_type(self):
        if not self._has_operator_info:
            self.__parse_operator_info()
        return self._op_type


class UnaryExpr(AbstractNode):
    pass


class UnaryOperator(AbstractNode):
    def __init__(self, kind, node, tu):
        super().__init__(kind, node, tu)
        self._has_operator_info = False
        self._op_sym_rng = None
        self._op_type = None

    def __parse_operator_info(self):
        childs = list(self.get_children())
        if len(childs) != 1:
            raise RuntimeError("Unary operators should only have one children _node")
        tokens = self.tokens()
        for pos, tok in enumerate(tokens):
            if tok.location() not in childs[0].text_range():
                self._op_sym_rng = tok.text_range()
                self._op_type = tok.text()
        if self._op_type is None:
            raise ParseError("Unable to determine the current operator:", self.text_range())
        self._has_operator_info = True

    def get_operator_symbol_range(self):
        if not self._has_operator_info:
            self.__parse_operator_info()
        return self._op_sym_rng

    def get_operator_type(self):
        if not self._has_operator_info:
            self.__parse_operator_info()
        return self._op_type

    def is_prefix_operator(self):
        if not self._has_operator_info:
            self.__parse_operator_info()
        # ToDo: proper checks for the ++ operator
        return self.get_operator_type() != "++"


class CompoundAssignmentOperator(AbstractNode):
    def __init__(self, kind, node, tu):
        super().__init__(kind, node, tu)
        self._has_operator_info = False
        self._op_sym_rng = None
        self._op_type = None

    def __parse_operator_info(self):
        children = list(self.get_children())
        if len(children) != 2:
            raise RuntimeError("Binary operators should only have two children nodes")
        tokens = self.tokens()
        for pos, tok in enumerate(tokens):
            loc = tok.location()
            if loc not in children[0].text_range() and loc not in children[1].text_range() and loc in self.text_range():
                self._op_sym_rng = tok.text_range()
                self._op_type = tok.text()
        if self._op_type is None:
            raise ParseError("Unable to determine the current operator:", self.text_range())
        self._has_operator_info = True

    def get_operator_symbol_range(self):
        if not self._has_operator_info:
            self.__parse_operator_info()
        return self._op_sym_rng

    def get_operator_type(self):
        if not self._has_operator_info:
            self.__parse_operator_info()
        return self._op_type


class ParamDecl(AbstractNode):
    def type(self) -> Type:
        return _wrap_type(self._node.type)


class VariableDecl(AbstractNode):
    def is_definition(self) -> bool:
        return NodeKind.VARIABLE_DEFINITION == self.kind()

    def is_static(self) -> bool:
        return self._node.storage_class == clang.cindex.StorageClass.STATIC

    def is_global(self) -> bool:
        return self._node.lexical_parent == self._translation_unit.cursor and not self.is_static()

    def type(self) -> Type:
        return _wrap_type(self._node.type)


class VariableDef(VariableDecl):
    pass


class FunctionDecl(AbstractNode):
    def is_static(self) -> bool:
        return self._node.storage_class == clang.cindex.StorageClass.STATIC

    def is_definition(self) -> bool:
        return self.kind() == NodeKind.FUNCTION_DEFINITION

    def get_parameters_declarations(self) -> Iterator[ParamDecl]:
        """Get an iterator over the declarations of this function's parameters"""
        return filter(lambda child: isinstance(child, ParamDecl), self.get_children())


class FunctionDef(FunctionDecl):
    def get_body_statement(self) -> CompoundStatement:
        """Get the compound statement describing the body of this function"""
        if not self.is_definition():
            raise RuntimeError("Function is not a definition")
        for child in self.get_children():
            if child.kind() == NodeKind.COMPOUND_STATEMENT:
                return child
        raise RuntimeError("No body found for function")


class TranslationUnit(AbstractNode):
    def filename(self):
        """The filename associated to this translation unit"""
        return os.path.basename(self._node.spelling)

    def fullpath(self):
        """The full path to the file associated to this translation unit"""
        return os.path.abspath(self._node.spelling)

    @property
    def raw_translation_unit(self):
        return self._node.translation_unit

    @property
    def raw_file(self):
        return self.raw_translation_unit.get_file(self._node.spelling)


class CompoundLiteralExpr(AbstractNode):
    pass


class InitListExpr(AbstractNode):
    pass


class ParenExpr(AbstractNode):
    pass


class CCastExpr(AbstractNode):
    pass


class DeclRefExpr(AbstractNode):
    def referenced_declaration(self):
        return _wrap_node(self._node.referenced(), self._translation_unit)


class ArraySubscriptExpr(AbstractNode):
    pass


class ControlStatement(AbstractNode):
    def has_no_body(self) -> bool:
        """
        Check whether the control statement has no body (not even an empty one)

        This matches statements like `while (cond);`
        """
        childs = list(self.get_children())
        return self.is_one_liner() and isinstance(childs[-1], NullStatement)

    def is_one_liner(self) -> bool:
        """
        Check whether the control statement is a one-liner

        This matches statements like `if (cond) return 1;`, along with statements without a body
        """
        rng = self.text_range()
        return rng.start.line == rng.end.line

    def has_single_statement_body(self) -> bool:
        """
        Check whether the control statement has a single-statement body

        This matches statements that have no body, those that are one-liners, and those like below:
        ```
        if (cond)
            return 1;
        ```
        """
        return not any(map(lambda node: isinstance(node, CompoundStatement), self.get_children()))


class IfStatement(ControlStatement):
    def has_then_branch(self) -> bool:
        nb_children = sum(1 for _ in self.get_children())
        return nb_children >= 2

    def get_then_branch(self):
        assert self.has_then_branch()
        children = list(self.get_children())
        return children[1]

    def has_else_branch(self) -> bool:
        nb_children = sum(1 for _ in self.get_children())
        return nb_children == 3

    def get_else_branch(self):
        assert self.has_else_branch()
        children = list(self.get_children())
        return children[-1]


class WhileStatement(ControlStatement):
    pass


class DoStatement(AbstractNode):
    pass


class ForStatement(ControlStatement):
    pass


class SwitchStatement(AbstractNode):
    pass


class CaseStatement(AbstractNode):
    pass


class DefaultStatement(AbstractNode):
    pass


class BreakStatement(AbstractNode):
    pass


class ContinueStatement(AbstractNode):
    pass


class DeclStatement(AbstractNode):
    pass


class NullStatement(AbstractNode):
    pass


class UnexposedExpr(AbstractNode):
    pass


class UnexposedAttr(AbstractNode):
    pass


class UnexposedStmt(AbstractNode):
    pass


class UnexposedDecl(AbstractNode):
    pass


class StatementExpr(AbstractNode):
    pass


class AsmStatement(AbstractNode):
    pass


class MacroInstantiation(AbstractNode):
    def has_visible_definition(self) -> bool:
        """Check whether the instantiated macro's definition can be retrieved"""
        return self._node.get_definition() is not None

    def get_definition(self) -> MacroDef:
        """Get the node corresponding to the instantiated macro's definition"""
        return _wrap_node(self._node.get_definition(), self._translation_unit)


class Ignored(AbstractNode):
    pass


class TranslationUnitVisitor:
    def __init__(self, filename, translation_unit):
        self._callbacks = {}
        self.filename = filename
        self._translation_unit = translation_unit

    def on(self, kind, callback):
        """
        Register a callback for a given kind of node

        :param kind:                the kind to register the callback for
        :param callback:            the callback to use for the kind
        """
        self._callbacks[kind] = callback
        return self

    def _traverse_nodes(self, translation_unit, node, depth=0):
        node_kind = _identify_node_kind(node)
        if node_kind != NodeKind.IGNORED:
            if (node.location.file is not None and node.location.file.name == self.filename) \
                    or NodeKind.TRANSLATION_UNIT == node_kind:
                node_info = _create_node_info(node_kind, node, translation_unit)
                yield node_info
        for child_node in node.get_children():
            yield from self._traverse_nodes(translation_unit, child_node, depth + 1)

    def visit(self):
        """
        Perform the visitation using the currently-registered callbacks
        """

        nodes = (node for node in self._traverse_nodes(self._translation_unit, self._translation_unit.cursor))
        for node in nodes:
            if node.kind() in self._callbacks:
                self._callbacks[node.kind()](node)

    def ast_root(self):
        """
        Retrieve the root of the AST
        """
        return _wrap_node(self._translation_unit.cursor, self._translation_unit)

    def nodes_with_kind(self, kind, *, only_in_current_file=True):
        def should_keep_node(node: AbstractNode):
            if node.kind() != kind:
                return False
            node_file = node.location().file
            if only_in_current_file and node_file is not None and node_file.name != self.filename:
                return False
            return True

        return filter(
            should_keep_node,
            (node for node in self._traverse_nodes(self._translation_unit, self._translation_unit.cursor))
        )


class FileProcessor:
    """
    Class responsible for AST traversals
    """

    def __init__(self, path: str, *, libclang_path: str = "/usr/local/lib/libclang.so"):
        """
        :param path:                the path to the file to process
        :param libclang_path:       the path to libclang.so
        """
        clang.cindex.Config.set_library_file(libclang_path)
        self.path = path
        self._translation_unit = None
        self._filename = None

    def process(self, include_dirs: List[str] = None, options: List[str] = None):
        """
        Load the file and process it

        :param include_dirs:        a list of directory to use as include directories
        :param options:             a list of compiler options to specify
        """
        options = ["-x", "c"] + (options or [])
        if include_dirs is not None:
            for inc_dir in include_dirs:
                options.append("-I" + inc_dir)
        try:
            index = clang.cindex.Index.create()
            self._translation_unit = index.parse(
                self.path,
                options,
                options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
            )
            self._filename = self._translation_unit.cursor.spelling
        except clang.cindex.TranslationUnitLoadError:
            raise TranslationUnitLoadError()

    def translation_unit_visitor(self):
        """
        Retrieve a visitor for the processed translation unit
        """
        return TranslationUnitVisitor(self._filename, self._translation_unit)
