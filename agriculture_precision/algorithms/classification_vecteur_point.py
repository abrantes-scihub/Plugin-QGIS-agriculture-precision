# -*- coding: utf-8 -*-

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



from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsApplication,
                       QgsRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterField,
                       QgsField,
                       QgsFeature,
                       QgsPointXY,
                       QgsGeometry,
                       QgsProcessingUtils)

from .functions.fonctions_repartition import *

from qgis import processing 
import numpy as np
import pandas as pd

class ClassificationVecteurPoint(QgsProcessingAlgorithm):
    """
    
    """
    
    OUTPUT= 'OUTPUT'
    INPUT = 'INPUT'
    INPUT_METHOD_CLASS = 'INPUT_METHOD_CLASS'
    INPUT_N_CLASS='INPUT_N_CLASS'
    INPUT_ECHANTILLON = 'INPUT_ECHANTILLON'
    FIELD = 'FIELD'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Vector to classify'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INPUT_METHOD_CLASS,
                self.tr('Classification method'),
                ['Quantiles', 'Equal-intervals']                
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_N_CLASS, 
                self.tr('Number of classes'),
                QgsProcessingParameterNumber.Integer,
                4,
                False,
                2,
                10
            )
        )
        
        self.addParameter( 
            QgsProcessingParameterField( 
                self.FIELD, 
                self.tr( "Field to classify" ), 
                QVariant(),
                self.INPUT,
                type=QgsProcessingParameterField.Numeric
            ) 
        )
    
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Classified vector')
            )
        )
        
        

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        
        layer=self.parameterAsVectorLayer(parameters,self.INPUT,context) 
        
        new_fields = layer.fields()
        new_fields.append(QgsField('Classes', QVariant.Double))
        
        
        (sink,fn) = self.parameterAsSink(parameters,self.OUTPUT,context, new_fields, layer.wkbType(), layer.sourceCrs())
        method = self.parameterAsEnum(parameters,self.INPUT_METHOD_CLASS,context)
                                   
        if feedback.isCanceled():
            return {}
                

              
        features = layer.getFeatures()
        
        #liste contenant les noms des champs
        field_list=[field.name() for field in layer.fields()]
        
        #on créé une matrice ou 1 ligne = 1 feature
        data = np.array([[feat[field_name] for field_name in field_list] for feat in features])
                
        #on créer le dataframe avec les données et les noms des colonnes
        df = pd.DataFrame(data, columns = field_list)
        
        array = df[parameters['FIELD']].values
        out_array = array[:]
                                           
        if feedback.isCanceled():
            return {}
                

        if method == 0 :
           out_array = rep_quantiles(parameters['INPUT_N_CLASS'],array,out_array)
        else :
           out_array = intervalles_egaux(parameters['INPUT_N_CLASS'],array,out_array)
           
        df['Classes']=out_array
        #on va créer un dataframe avec les coordonnées, normalement les features sont parcourrues dans le même ordre
        features = layer.getFeatures()
        coordinates_arr = np.array([[feat.geometry().asPoint()[k] for k in range(2)] for feat in features])
        coordinates = pd.DataFrame(coordinates_arr, columns = ['X','Y'])
        df['X']=coordinates['X']
        df['Y']=coordinates['Y']    
        
        #on transforme le dataframe en liste pour les attributs
        df_list=df.values.tolist()
        
        featureList=[]
                                           
        if feedback.isCanceled():
            return {}
                

        #on va parcourrir chaque ligne, ie chaque feature
        for row in df_list:
            feat = QgsFeature()
            feat.setAttributes(row[0:-2]) #row = une ligne, on exclu les deux dernières colonnes qui sont les coordonnées
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(row[-2],row[-1]))) #on définit la position de chaque point 
            featureList.append(feat) #on ajoute la feature à la liste

        #on ajoute la liste des features à la couche de sortie
        sink.addFeatures(featureList)
                                           
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
        return "V - Classification"

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
        return self.tr('Classification')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'classification'
    
    def shortHelpString(self):
        short_help = self.tr(
            'Allows to reclassify a vector with point geometry into a user-'
            'defined number of classes using several classification methods'
            '\n provided by ASPEXIT\n'
            'author : Lisa Rollier'
        )
        return short_help


    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ClassificationVecteurPoint()
