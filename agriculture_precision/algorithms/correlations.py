## -*- coding: utf-8 -*-

"""
/***************************************************************************
 Precision Agriculture
                                 A QGIS plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-07-21
        copyright            : (C) 2020 by ASPEXIT
        email                : cleroux@aspexit.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Lisa Rollier - ASPEXIT'
__date__ = '2020-07-21'
__copyright__ = '(C) 2020 by ASPEXIT'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'



from qgis.PyQt.QtCore import QCoreApplication#, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsApplication,
                       QgsVectorLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterEnum)

from qgis import processing 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Correlation(QgsProcessingAlgorithm):
    """
    
    """ 

    OUTPUT= 'OUTPUT'
    INPUT = 'INPUT'
    FIELD = 'FIELD'
    INPUT_METHOD = 'INPUT_METHOD'
    INPUT_CONFIANCE = 'INPUT_CONFIANCE'
    method_names = ['pearson','kendall','spearman']

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Vector layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INPUT_METHOD,
                self.tr('Correlation index'),
                self.method_names
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT,
                self.tr('Correlation plot'),
            )
        )
        
        

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        
        layer=self.parameterAsVectorLayer(parameters,self.INPUT,context) 
        fn = self.parameterAsFileOutput(parameters,self.OUTPUT,context)
        method=self.parameterAsEnum(parameters,self.INPUT_METHOD,context)
                                           
        if feedback.isCanceled():
            return {}
                

        features = layer.getFeatures()
       
        #liste contenant les noms des champs
        field_list=[field.name() for field in layer.fields() if field.type() in [2,4,6]] #peut-être qu'il y a d'autres types numériques... difficile a trouver
        
        #on créé une matrice ou 1 ligne = 1 feature
        data = np.array([[feat[field_name] for field_name in field_list] for feat in features])
                
        #on créer le dataframe avec les données et les noms des colonnes
        df = pd.DataFrame(data, columns = field_list)
        
        #on créer la matrice des graphiques de corrélation
        axes = pd.plotting.scatter_matrix(df,alpha=0.2)
        
        #on ajoute un titre au graphique
        plt.suptitle(layer.name()+'_'+self.method_names[method])
        
        #on créer une matrice numpy avec les corrélations
        corr = df.corr(self.method_names[method])
        corr=corr.to_numpy()
                                           
        if feedback.isCanceled():
            return {}
                

        # on ajoute les corrélations dans la partie supérieure de la matrice des graphiques de corrélation
        for i, j in zip(* np.triu_indices_from(axes, k=1)):
            axes[i, j].annotate("%.3f" %corr[i,j], (0.8, 0.8), xycoords='axes fraction', ha='center', va='center')
        
        #on sauvegarde dans l'adresse en sortie
        plt.savefig(fn+'\\figure_correlation_' + self.method_names[method] + '_' + layer.name() +'.jpg')
                                           
        if feedback.isCanceled():
            return {}
                

        return{self.OUTPUT : fn} 
      

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'V - Correlation coefficient'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Correlation')
    
    def shortHelpString(self):
        short_help = self.tr(
            'Allows to calculate a correlation index across numerical '
            'columns of the input vector layer. A correlation plot is produced.'
            '\n provided by ASPEXIT\n'
            'author : Lisa Rollier'
        )
        return short_help
        
    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'correlation'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Correlation()
