from Qt import QtGui, QtCore, QtWidgets


class NumberBar(QtWidgets.QWidget):
    def __init__(self, edit):
        QtWidgets.QWidget.__init__(self, edit)
        self.edit = edit
        self.adjustWidth(1)

    def paintEvent(self, event):
        self.edit.numberbarPaint(self, event)
        QtWidgets.QWidget.paintEvent(self, event)

    def adjustWidth(self, count):
        width = self.edit.fontMetrics().width(unicode(count))
        if self.width() != width:
            self.setFixedWidth(width)

    def updateContents(self, rect, scroll):
        if scroll:
            self.scroll(0, scroll)
        else:
            self.update()


class DictionaryCompleter(QtWidgets.QCompleter):
    def __init__(self, code, parent=None):
        liste = [x for x in code.words]
        liste.extend(code.sentences)
        QtWidgets.QCompleter.__init__(self, liste, parent)


class MultiEditor(QtWidgets.QWidget):
    textChanged = QtCore.Signal()

    def __init__(self, defPath, parent=None):
        super(MultiEditor, self).__init__(parent)
        self.number_bar = None
        self.defPath = defPath
        
        self.types = self.readDefinitions()
        code = self.types[0]

        completer = DictionaryCompleter(code)
        self.text = CompletionTextEdit(self)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.text.setFont(font)
        high = Highlighter(code.words, self.text.document())
        self.text.highlighter = high
        self.text.setCompleter(completer)
        
        self.number_bar = NumberBar(self.text)
        self.text.numberBar = self.number_bar
        self.text.connectNumberBar()
    
        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.text)

        self.setLayout(hbox)
        self.text.textChanged.connect(self.valueChanged)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_F:
            self.find()
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_R:
            self.replace()
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_G:
            self.goto()

    def setReadOnly(self, value):
        self.text.setReadOnly(value)

    def valueChanged(self):
        self.textChanged.emit()

    def setText(self, txt):
        self.text.setPlainText(txt)

    def toPlainText(self):
        return self.text.toPlainText()

    def setPlainText(self, txt):
        self.text.setPlainText(txt)

    def find(self):
        s = self.text.textCursor().selectedText()
        d = FindGui(self.text, s, parent=self)

    def goto(self):
        d = GotoGui(self.text, parent=self)
    
    def replace(self):
        s = self.text.textCursor().selectedText()
        d = ReplaceGui(self.text, s, parent=self)

    def readDefinitions(self):
        types = []
        with open(self.defPath, "r") as f:
            lines = f.readlines()
            typeEnCours = None
            listeEnCours = []
            i = 0
            while i < len(lines):
                if lines[i][0] == '#':
                    found = 0
                    for x in types:
                        if x.name == lines[i].strip().split()[0][1:]:
                            typeEnCours = x
                            found = 1
                            break
                    if not found:
                        typeEnCours = QtEditType()
                        typeEnCours.name = lines[i].strip().split()[0][1:]
                        types.append(typeEnCours)

                    if lines[i].strip().split()[1] == "words":
                        listeEnCours = typeEnCours.words
                    if lines[i].strip().split()[1] == "sentences":
                        listeEnCours = typeEnCours.sentences
                    
                elif len(lines[i].strip()):
                    listeEnCours.append(lines[i].strip())
                i += 1
            for type in types:
                type.words.sort()
                type.sentences.sort()
        return types


class AltTabPressEater2(QtCore.QObject):
    def eventFilter(self, obj, event):
        if hasattr(event, "key"):
            if event.key() == QtCore.Qt.Key_Tab:
                return True
        return QtCore.QObject.eventFilter(self, obj, event)


class CompletionTextEdit(QtWidgets.QPlainTextEdit):
    editingFinished = QtCore.Signal()

    def __init__(self, parent=None):
        super(CompletionTextEdit, self).__init__(parent)
        self.setMinimumWidth(400)
        self.setTabStopWidth(30)
        self.completer = None
        self.highlighter = None
        self.specialRule = None
        self.moveCursor(QtGui.QTextCursor.End)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.numberBar = None
        self.cursorPositionChanged.connect(self.highlight)
        self.highlight()
        self.setTabChangesFocus(False)
        self.font_size = 11
        self.style = "background-color: #272822; color: #f8f8f2; font: {0}pt 'DejaVu Sans Mono'"
        self.setStyleSheet(self.style.format(self.font_size))

    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.delta() > 0:
                self.font_size += 1
            elif self.font_size > 5:
                self.font_size -= 1
            self.setStyleSheet(self.style.format(self.font_size))
        else:
            QtWidgets.QPlainTextEdit.wheelEvent(self, event)

    def focusOutEvent(self, event):
        QtWidgets.QPlainTextEdit.focusOutEvent(self, event)
        self.editingFinished.emit()

    def connectNumberBar(self):
        self.blockCountChanged.connect(self.numberBar.adjustWidth)
        self.updateRequest.connect(self.numberBar.updateContents)
        self.numberBar.adjustWidth(self.blockCount())

    def highlight(self):
        hi_selection = QtWidgets.QTextEdit.ExtraSelection()
        hi_selection.format.setBackground(QtGui.QColor("#3e3d32"))
        hi_selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        hi_selection.cursor = self.textCursor()
        hi_selection.cursor.clearSelection()
        self.setExtraSelections([hi_selection])

    def numberbarPaint(self, number_bar, event):
        font_metrics = self.fontMetrics()
        current_line = self.document().findBlock(self.textCursor().position()).blockNumber() + 1
        block = self.firstVisibleBlock()
        line_count = block.blockNumber()
        painter = QtGui.QPainter(number_bar)
        painter.setFont(self.font())
        pen = QtGui.QPen()
        while block.isValid():
            line_count += 1
            block_top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
            if not block.isVisible() or block_top == event.rect().bottom():
                break
            if line_count == current_line:
                pen.setColor(QtGui.QColor("#75715e"))
                painter.setPen(pen)
            else:
                pen.setColor(QtGui.QColor("#5B5B5B"))
                painter.setPen(pen)
            paint_rect = QtCore.QRect(0, block_top+2, number_bar.width(), font_metrics.height())
            painter.drawText(paint_rect, QtCore.Qt.AlignRight, unicode(line_count))
            block = block.next()
        painter.end()

    def findNext(self, str):
        self.find(str)
    
    def findPrev(self, str):
        self.find(str, QtWidgets.QTextDocument.FindBackward)

    def replaceNext(self, strA, strB):
        if self.find(strA):
            curs = self.textCursor()
            curs.insertText(strB)
            
            curs.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
            self.setTextCursor(curs)
            self.find(strB)

    def replaceAll(self, strA, strB):
        if strA != strB:
            curs = self.textCursor()
            curs.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
            self.setTextCursor(curs)
            while self.find(strA):
                curs = self.textCursor()
                curs.insertText(strB)
                self.setTextCursor(curs)    
            curs.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
            self.setTextCursor(curs)
            self.find(strB)

    def replaceBlock(self, strA, strB):
        if strA != strB:
            curs = self.textCursor()
            startPos = curs.anchor()
            endPos = curs.position()
            curs.setPosition(startPos, QtGui.QTextCursor.MoveAnchor)
            self.setTextCursor(curs)
            while self.find(strA):
                curs = self.textCursor()
                if curs.position() > endPos:
                    break
                curs.insertText(strB)
                self.setTextCursor(curs)    
            curs.setPosition(startPos, QtGui.QTextCursor.MoveAnchor)
            curs.setPosition(endPos, QtGui.QTextCursor.KeepAnchor)
            self.setTextCursor(curs)

    def replaceAllExp(self, strA, strB):
        text_to_find = QtCore.QRegExp(strA, QtCore.Qt.CaseSensitive)

        find_result = self.document().find(text_to_find)
        if not find_result.isNull():
            cursA = self.textCursor()
            posA = self.verticalScrollBar().value()
            while not find_result.isNull():
                self.setTextCursor(find_result)
                curs = self.textCursor()
                curs.insertText(strB)
                self.setTextCursor(curs)
                find_result = self.document().find(text_to_find)
            self.setTextCursor(cursA)
            self.verticalScrollBar().setValue(posA)
        
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.setStyleSheet("QMenu::item:selected {color: #FFFFFF; background-color: #888888;}")
        menu.exec_(event.globalPos())

    def toggleSelectionComment(self):
        curs = self.textCursor()
        # Sets
        mode = 0
        
        spos = curs.position()
        epos = curs.anchor()
        if spos > epos:
            hold = spos
            spos = epos
            epos = hold
        curs.setPosition(spos, QtGui.QTextCursor.MoveAnchor)
        
        if len(curs.block().text()):
            mode = (curs.block().text()[0] == '#')

        sblock = curs.block().blockNumber()
        curs.setPosition(epos, QtGui.QTextCursor.MoveAnchor)
        eblock = curs.block().blockNumber()

        # Start modifications
        curs.setPosition(spos, QtGui.QTextCursor.MoveAnchor)
        curs.beginEditBlock()
        for i in range(0, eblock-sblock+1):
            curs.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
            if mode:
                if len(curs.block().text()):
                    if curs.block().text()[0] == '#':
                        curs.deleteChar()
                        if len(curs.block().text()):
                            if curs.block().text()[0] == ' ':
                                curs.deleteChar()
            else:
                curs.insertText("# ")
            curs.movePosition(QtGui.QTextCursor.NextBlock, QtGui.QTextCursor.MoveAnchor)
        curs.endEditBlock()

        # Set our cursor's selection to span all of the involved lines.
        curs.setPosition(spos, QtGui.QTextCursor.MoveAnchor)
        curs.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
        while curs.block().blockNumber() < eblock:
            curs.movePosition(QtGui.QTextCursor.NextBlock, QtGui.QTextCursor.KeepAnchor)
        curs.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)

        # Done!
        self.setTextCursor(curs)

    def setCompleter(self, completer):
        if self.completer:
            self.disconnect(self.completer, 0, self, 0)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer = completer
        self.completer.activated[str].connect(self.insertCompletion)

    def insertCompletion(self, completion):
        if completion == self.completer.completionPrefix():
            return
        tc = self.textCursor()
        extra = (len(completion) - len(self.completer.completionPrefix()))
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()

        pos = tc.position()
        while pos > 0:
            pos -= 1
            char = self.document().toPlainText()[pos]
            char = char.encode('utf-8')
            eow = "~!@#$%^&*()_+{}|:<>?,/;'\n[]\\= "  # end of word
            if char in eow:
                break
            tc.setPosition(pos, QtGui.QTextCursor.KeepAnchor)

        return tc.selectedText()

    def mousePressEvent(self, event):
        super(CompletionTextEdit, self).mousePressEvent(event)
        if self.specialRule:
            self.highlighter.highlightingRules.remove(self.specialRule)
            self.specialRule = None
            self.highlighter.setDocument(self.document())

    def mouseDoubleClickEvent(self, event):
        super(CompletionTextEdit, self).mouseDoubleClickEvent(event)

        word = self.textCursor().selectedText()
        if len(word):
            keywordFormat = QtGui.QTextCharFormat()
            keywordFormat.setForeground(QtGui.QColor("#FF00BB"))
            rule = (QtCore.QRegExp("\\b%s\\b" % word), keywordFormat)
            self.specialRule = rule
            self.highlighter.highlightingRules.append(rule) 
            self.highlighter.setDocument(self.document())

    def keyPressEvent(self, event):
        ok = 1

        if len(self.textCursor().selectedText()) and event.key() == 16777218:
            self.indent("left")
            return
        if len(self.textCursor().selectedText()) and event.key() == QtCore.Qt.Key_Tab:
            self.indent("right")
            return
        
        if self.completer:
            if self.completer.popup().isVisible():
                ok = 0
        if event.key() == QtCore.Qt.Key_Escape and ok == 1:
            self.toggleSelectionComment()
            return

        if self.completer:
            if self.completer.popup().isVisible():
                if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Escape, QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab):
                    event.ignore()
                    return

        # has ctrl-E been pressed??
        isShortcut = (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_E)
        if not self.completer or not isShortcut:
            if event.key() == QtCore.Qt.Key_Tab:
                tc = self.textCursor()
                tc.insertText('    ')
                self.setTextCursor(tc)
            else:
                QtWidgets.QPlainTextEdit.keyPressEvent(self, event)

        # ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier, QtCore.Qt.ShiftModifier)
        if ctrlOrShift and str(event.text()) == '':
            # ctrl or shift key on it's own
            return

        eow = "~!@#$%^&*()_+{}|:<>?,./;'[]\\="# end of word

        completionPrefix = self.textUnderCursor()

        if not isShortcut:
            hasModifier = event.modifiers() in (QtCore.Qt.ControlModifier, QtCore.Qt.AltModifier)
            if hasModifier or event.text().encode('utf-8') == '' or len(completionPrefix) < 3 or event.text().encode('utf-8')[-1] in eow:
                if self.completer:
                    self.completer.popup().hide()
                    return

        if self.completer:
            if completionPrefix != self.completer.completionPrefix():
                self.completer.setCompletionPrefix(completionPrefix)
                popup = self.completer.popup()
                popup.setCurrentIndex(self.completer.completionModel().index(0, 0))

                cr = self.cursorRect()
                cr.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
                self.completer.complete(cr)  # popup it up!

    def indent(self, dir):
        curs = self.textCursor()        
        spos = curs.position()
        epos = curs.anchor()
        if spos > epos:
            hold = spos
            spos = epos
            epos = hold
        curs.setPosition(spos, QtGui.QTextCursor.MoveAnchor)

        sblock = curs.block().blockNumber()
        curs.setPosition(epos, QtGui.QTextCursor.MoveAnchor)
        eblock = curs.block().blockNumber()

        # Start modifications
        curs.setPosition(spos, QtGui.QTextCursor.MoveAnchor)
        curs.beginEditBlock()
        for i in range(0, eblock-sblock+1):
            curs.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
            if dir == 'left':
                if len(curs.block().text()):
                    if curs.block().text()[0] == '\t':
                        curs.deleteChar()
                    elif curs.block().text()[:4] == ' '*4:
                        [curs.deleteChar() for i in range(4)]
            else:
                curs.insertText(' '*4)
            curs.movePosition(QtGui.QTextCursor.NextBlock, QtGui.QTextCursor.MoveAnchor)
        curs.endEditBlock()

        # Set our cursor's selection to span all of the involved lines.
        curs.setPosition(spos, QtGui.QTextCursor.MoveAnchor)
        curs.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
        while curs.block().blockNumber() < eblock:
            curs.movePosition(QtGui.QTextCursor.NextBlock, QtGui.QTextCursor.KeepAnchor)
        curs.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)

        # Done!
        self.setTextCursor(curs)


class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, words, parent=None):
        super(Highlighter, self).__init__(parent)
        self.highlightingRules = []
        self.auto = True

        w = list(words)
        ops = ['\+', '\*', '\/', '\%', '\-', '\=', '\!\=', '\<', '\>', '\<\=', '\>\=']
        vals = ['True', 'False', 'None']
        keywordPatterns = ["\\b%s\\b" % x for x in w]
        opsPatterns = ["%s" % x for x in ops]
        valPatterns = ["%s" % x for x in vals]

        # OPERATOR
        opFormat = QtGui.QTextCharFormat()
        opFormat.setForeground(QtGui.QColor("#f92672"))
        self.highlightingRules = [(QtCore.QRegExp(pattern), opFormat) for pattern in opsPatterns]

        # NOMBRES
        numFormat = QtGui.QTextCharFormat()
        numFormat.setForeground(QtGui.QColor("#ae81ff"))
        self.highlightingRules.append((QtCore.QRegExp("\\b[0-9|\.]+"), numFormat))

        # FONCTIONS
        functionFormat = QtGui.QTextCharFormat()
        functionFormat.setFontItalic(True)
        functionFormat.setForeground(QtGui.QColor("#66d9ef"))
        self.highlightingRules.append((QtCore.QRegExp("\\b[A-Za-z0-9_]+(?=\\()"), functionFormat))

        # DEF
        defFormat = QtGui.QTextCharFormat()
        defFormat.setFontItalic(True)
        defFormat.setForeground(QtGui.QColor("#a6e22e"))
        self.highlightingRules.append((QtCore.QRegExp("\\bdef\\b\\s*(\\w+)"), defFormat))
        self.highlightingRules.append((QtCore.QRegExp("\\bclass\\b\\s*(\\w+)"), defFormat))

        # KEYWORD
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtGui.QColor("#f92672"))
        self.highlightingRules.extend([(QtCore.QRegExp(pattern), keywordFormat) for pattern in keywordPatterns])

        # VALUES
        valueFormat = QtGui.QTextCharFormat()
        valueFormat.setForeground(QtGui.QColor("#ae81ff"))
        self.highlightingRules.extend([(QtCore.QRegExp(pattern), valueFormat) for pattern in valPatterns])

        # STRINGS
        quotationFormat = QtGui.QTextCharFormat()
        quotationFormat.setForeground(QtGui.QColor("#e0d571"))
        self.highlightingRules.append((QtCore.QRegExp('"[^"]*"'), quotationFormat))
        self.highlightingRules.append((QtCore.QRegExp("'[^']*'"), quotationFormat))
        self.tri_single = (QtCore.QRegExp("'''"), 1, quotationFormat)
        self.tri_double = (QtCore.QRegExp('"""'), 2, quotationFormat)

        # COMMENT
        singleLineCommentFormat = QtGui.QTextCharFormat()
        singleLineCommentFormat.setForeground(QtGui.QColor("#75715e"))
        self.highlightingRules.append((QtCore.QRegExp("#.*$"), singleLineCommentFormat))

        self.auto = False

    def highlightBlock(self, text):
        if not self.auto:
            for pattern, format in self.highlightingRules:
                expression = QtCore.QRegExp(pattern)
                index = expression.indexIn(text)
                while index >= 0:
                    length = expression.matchedLength()
                    self.setFormat(index, length, format)
                    index = expression.indexIn(text, index + length)

            self.setCurrentBlockState(0)

            # Do multi-line strings
            in_multiline = self.match_multiline(text, *self.tri_single)
            if not in_multiline:
                in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False


class QtEditType(object):
    def __init__(self):
        self.name = ""
        self.words = []
        self.sentences = []


class GotoGui(QtWidgets.QDialog):
    def __init__(self, edit, parent=None):
        super(GotoGui, self).__init__(parent)
        self.text = edit
        self.line = QtWidgets.QLineEdit()
        self.line.setValidator(QtWidgets.QIntValidator())
        b1 = QtWidgets.QPushButton('Go')
        layoutV = QtWidgets.QVBoxLayout()
        layoutV.addWidget(self.line)
        layoutV.addWidget(b1)

        b1.clicked.connect(self.go)

        self.setLayout(layoutV)
        self.setWindowTitle('Go to line...')
        self.resize(200, 100)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint)
        self.setModal(0)
        self.show()

    def go(self):
        num = int(self.line.text())-1
        text_block = self.text.document().findBlockByLineNumber(num)
        text_cursor = self.text.textCursor()
        text_cursor.setPosition(text_block.position())
        self.text.setFocus()
        self.text.setTextCursor(text_cursor)
        self.close()


class FindGui(QtWidgets.QDialog):
    def __init__(self, edit, s, parent=None):
        super(FindGui, self).__init__(parent)
        self.text = edit
        self.line = QtWidgets.QLineEdit(s)
        b1 = QtWidgets.QPushButton('Find next')
        b2 = QtWidgets.QPushButton('Find prev')
        layoutV = QtWidgets.QVBoxLayout()
        layoutH = QtWidgets.QHBoxLayout()
        layoutH.addWidget(b2)
        layoutH.addWidget(b1)
        layoutV.addWidget(self.line)
        layoutV.addLayout(layoutH)

        b1.clicked.connect(self.findNext)
        b2.clicked.connect(self.findPrev)

        self.setLayout(layoutV)
        self.setWindowTitle('Find...')
        self.resize(200, 70)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint)
        self.setModal(0)
        self.show()

    def findNext(self):
        text = self.line.text()
        self.text.findNext(text)

    def findPrev(self):
        text = self.line.text()
        self.text.findPrev(text)


class ReplaceGui(QtWidgets.QDialog):
    def __init__(self, edit, s, parent=None):
        super(ReplaceGui, self).__init__(parent)
        self.text = edit
        self.line1 = QtWidgets.QLineEdit(s)
        text2 = QtWidgets.QLabel('Replaced with')
        self.line2 = QtWidgets.QLineEdit()
        b1 = QtWidgets.QPushButton('Replace next')
        b2 = QtWidgets.QPushButton('Replace all')
        b4 = QtWidgets.QPushButton('Replace in sel')
        layoutV = QtWidgets.QVBoxLayout()
        layoutH = QtWidgets.QHBoxLayout()
        layoutH.addWidget(b1)
        layoutH.addWidget(b2)
        layoutH.addWidget(b4)
        layoutV.addWidget(self.line1)
        layoutV.addWidget(text2)
        layoutV.addWidget(self.line2)
        layoutV.addLayout(layoutH)

        b1.clicked.connect(self.replaceNext)
        b2.clicked.connect(self.replaceAll)
        b4.clicked.connect(self.replaceBlock)

        self.setLayout(layoutV)
        self.setWindowTitle('Replace...')
        self.resize(200, 120)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint)
        self.setModal(0)
        self.show()

    def replaceNext(self):
        textA = self.line1.text()
        textB = self.line2.text()
        self.text.replaceNext(textA, textB)

    def replaceAll(self):
        textA = self.line1.text()
        textB = self.line2.text()
        self.text.replaceAll(textA, textB)

    def replaceBlock(self):
        textA = self.line1.text()
        textB = self.line2.text()
        self.text.replaceBlock(textA, textB)
