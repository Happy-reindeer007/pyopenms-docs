import sys
import pyqtgraph as pg
import pyopenms
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QFont, QFontMetricsF, QPainter, QColor, QPen, QBrush, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout


class peptide_window(QWidget):

    HEIGHT = 200
    WIDTH = 400

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Peptide Viewer')

        self.layout = QHBoxLayout(self)
        self.pep = observed_peptide()

        # array starting with 1 and ends with len(seq)
        self.pep.setSequence("PEPTIDE")
        #self.pep.setPrefix({i: ["a%s"% (str(i))] for i in range(1, len(self.pep.sequence))}) #test sequence
        self.pep.setPrefix({1: ["a1", "b1"], 2: ["a2", "b2", "c2"]})
        self.pep.setSuffix({2: ["a2", "b2"], 4: ["a4", "b4", "c4"]})

        self.pep.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.pep.setMinimumSize(400,400)
        self.layout.addItem(QSpacerItem(40,50, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum))
        self.layout.addWidget(self.pep)
        self.layout.addItem(QSpacerItem(40,50, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum))

        # resize window to fit peptide size
        self.__resize()

        #self.setStyleSheet("background-color:white;");
        self.show()

    def __resize(self):
        if len(self.pep.sequence) > 15:
            peptide_window.WIDTH += ((len(self.pep.sequence) - 15) * 2*18)


class observed_peptide(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.resize(self.sizeHint())

    def initUI(self):

        self.sequence = ""
        self.suffix = {}
        self.prefix = {}

    def setSequence(self, seq):
        self.sequence = seq


    def setSuffix(self, lst):
        self.suffix = lst

    def setPrefix(self, lst):
        self.prefix = lst


    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.fillRect(event.rect(), QBrush(Qt.white))
        self.__drawPeptide(qp)
        qp.end()

    def __drawPeptide(self, qp):
        qp.setWindow(0, 0, peptide_window.WIDTH, peptide_window.HEIGHT)
        qp.setPen(QColor(168, 34, 3))
        qp.setFont(self.__getFont_Pep())

        self.__fragmentPeptide(qp)

    def __fragmentPeptide(self, qp):
        SPACE = 8

        if self.sequence != "":
            seq = list(self.sequence)
            dict_seq = {i: seq[i] for i in range(0, len(seq))}

            metrics = QFontMetricsF(self.__getFont_Pep())

            blank = 0
            for i, s in dict_seq.items():
                i_rev = self.__getReverseIndex(i, dict_seq)

                width = metrics.boundingRect(s).width()
                height = metrics.boundingRect(s).height()

                seq_len = len(self.sequence)
                start_point = (peptide_window.WIDTH - (seq_len * 17 + SPACE * (seq_len - 2)))/2
                # position of char
                position = QPointF(start_point + blank, (peptide_window.HEIGHT/2 + height/4))
                qp.drawText(position, s)

                # position lines
                center = (peptide_window.HEIGHT / 2)

                if s == "I":
                    pos_start = QPointF(start_point + blank - SPACE/2 + 2, center - height/2 - 2.5)
                else:
                    pos_start = QPointF(start_point + blank - SPACE/2, center - height/2 - 2.5)

                pos_end = QPointF(pos_start.x(), center + height/2)

                qp.setPen(self.__getPen())
                qp.setFont(self.__getFont_Ion())
                metrics_ion = QFontMetricsF(self.__getFont_Ion())


                if i in self.prefix:
                    qp.drawLine(pos_start, pos_end)
                    pos_left = QPointF(pos_end.x() - 2*SPACE, pos_end.y())
                    qp.drawLine(pos_end, pos_left)

                    prefix_ions = sorted(self.prefix[i])
                    blank_ion = 10

                    # add ions
                    for ion in prefix_ions:
                        height_ion = metrics_ion.boundingRect(ion).height()
                        pos_ion = QPointF(pos_left.x(), pos_left.y() + blank_ion)
                        qp.drawText(pos_ion, ion)
                        blank_ion += height_ion


                # for given line of existing prefix, expand with given suffix
                if i in self.prefix and i_rev in self.suffix :
                    pos_right = QPointF(pos_start.x() + 2*SPACE, pos_start.y())
                    qp.drawLine(pos_start, pos_right)

                    suffix_ions = sorted(self.suffix[i_rev], reverse=True)
                    blank_ion = 5

                    for ion in suffix_ions:
                        height_ion = metrics_ion.boundingRect(ion).height()
                        pos_ion = QPointF(pos_end.x() + 2.5, pos_right.y() - blank_ion)
                        qp.drawText(pos_ion, ion)
                        blank_ion += height_ion

                elif i_rev in self.suffix and i not in self.prefix:
                    qp.drawLine(pos_start, pos_end)
                    pos_right = QPointF(pos_start.x() + 2*SPACE, pos_start.y())
                    qp.drawLine(pos_start, pos_right)

                    suffix_ions = sorted(self.suffix[i_rev], reverse=True)
                    blank_ion = 5

                    for ion in suffix_ions:
                        height_ion = metrics_ion.boundingRect(ion).height()
                        pos_ion = QPointF(pos_end.x() + 2.5, pos_right.y() - blank_ion)
                        qp.drawText(pos_ion, ion)
                        blank_ion += height_ion

                blank += width + SPACE
                qp.setFont(self.__getFont_Pep())


    def __getFont_Pep(self):
        font = QFont("Courier")
        font.setStyleHint(QFont.TypeWriter)
        font.setPixelSize(30)
        return font

    def __getFont_Ion(self):
        font = QFont("Courier")
        font.setStyleHint(QFont.TypeWriter)
        font.setPixelSize(10)
        return font

    def __getPen(self):
        # style settings for the lines
        pen = QPen(QColor(168, 34, 3), 0.75, Qt.SolidLine)
        pen.setStyle(Qt.DashDotLine)
        return pen

    def __getReverseIndex(self, i, dict_seq):
        i_rev = 0
        if i != 0:
            i_rev = list(dict_seq.keys())[-i]
        return i_rev


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = peptide_window()
    sys.exit(app.exec_())
