import numpy as np


crystal_width = 10 * 0.001 # m
crystal_height = 30 * 0.001 # m
crystal_depth = 10 * 0.001 # m

lithium_6_enrichment = 0.95 # fraction (95% enriched)

front_face_distance = 80.4 * 0.01 # m

radiusTerm = ((crystal_width/2)**2)/2
heightTerm = ((crystal_height)**2)/12
centerTerm = (front_face_distance+(crystal_height/2))**2

avgDist = np.sqrt(radiusTerm+heightTerm+centerTerm)

#assuming d>>a

fractionalSolidAngle = ((crystal_depth/2)**2)/(4*(avgDist**2))
print(fractionalSolidAngle)