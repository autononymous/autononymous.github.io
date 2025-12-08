# -*- coding: utf-8 -*-
"""
@file pact_maths.py
@author Ryan Kissinger

@brief Mathematical functions, mostly based around array manipulation.
"""
##|=========================================================================|##
##|                                                                         |##
##|                            ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                              |##
##|                           ▒▒             ▒▒                             |##
##|                        ▒▒   █████████████   ▒▒                          |##
##|                      ▒▒▒  █████████████████  ▒▒▒                        |##
##|                     ▒▒▒▒ ████████   ████████ ▒▒▒▒                       |##
##|                     ▒▒▒  ████████             ▒▒▒                       |##
##|                     ▒▒▒  ███████████████████  ▒▒▒                       |##
##|                     ▒▒▒             ████████  ▒▒▒                       |##
##|                     ▒▒▒▒ ████████   ████████ ▒▒▒▒                       |##
##|                      ▒▒▒  █████████████████  ▒▒▒                        |##
##|                        ▒▒   █████████████   ▒▒                          |##
##|                           ▒▒             ▒▒                             |##
##|                            ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒                              |##
##|                                                                         |##
##|=========================================================================|##
##|                    ░█▀█▀█░█▀█░▀█▀░█░█░█▀▀░░░░█▀█░█░█░                   |##
##|                    ░█░█░█░█▀█░░█░░█▀█░▀▀█░░░░█▀▀░░█░░                   |##
##|                    ░▀░▀░▀░▀░▀░░▀░░▀░▀░▀▀▀░▀░░▀░░░░▀░░                   |##
##|=========================================================================|##
##|            :                                                            |##
##|   PROJECT <|> Project "PACT" -- Plate Alignment Calibration Tool        |##
##|            :  AKA the "Pre-Registration Fixture"                        |##
##|            :                                                            |##
##|   COMPANY <|> STOLLE MACHINERY COMPANY, LLC                             |##
##|            :  6949 S. POTOMAC STREET                                    |##
##|            :  CENTENNIAL, COLORADO, 80112                               |##
##|            :                                                            |##
##|      FILE <|> pact_maths.py                                             |##
##|            :                                                            |##
##|    AUTHOR <|> Ryan Kissinger                                            |##
##|            :                                                            |##
##|   VERSION <|> '-' - 09/29/25                                            |##
##|            :                                                            |##
##|-------------------------------------------------------------------------|##
##|            :                                                            |##
##|   PURPOSE <|> Math.                                                     |##
##|            :                                                            |##
##|   LICENSE <|> Copyright (C) Stolle Machinery Company                    |##
##|            :  All Rights Reserved                                       |##
##|            :                                                            |##
##|           <|> This source code is protected under international         |##
##|            :  copyright law. All rights reserved and protected by the   |##
##|            :  copyright holders. This file is confidential and only     |##
##|            :  available to authorized individuals with the permission   |##
##|            :  of the copyright holders.  If you encounter this file     |##
##|            :  and do not have permission, please contact the copyright  |##
##|            :  holders and delete this file.                             |##
##|            :                                                            |##
##|=========================================================================|##
import numpy as np

def CrossProd(A,B):
    '''! Take the cross product of two arrays; A x B.
    @param A  First matrix.
    @param B  Second matrix.
    @return  Cross product of A and B.'''  
    # Get dimensions of matrices.
    Ax = np.size(A,0);
    Ay = np.size(A,1);
    Bx = np.size(B,0);
    By = np.size(B,1);
    # Instantiate our return matrix with the final size needed.
    result = np.zeros([Ax,By]);
    # How a cross product works.
    for i in range(Ax):
        for j in range(By):
            for k in range(Ay):
                result[i,j] = result[i,j] + ( A[i,k] * B[k,j] )
    return result

def Hmat_Z(rot,xp=0,yp=0,zp=0):
    '''! Return Jacobian transformation matrix, rotating about Z-axis.
         @param rot  Rotation in RADIANS.
         @param xp  X-displacement.
         @param yp  Y-displacement.
         @param zp  Z-displacement.'''
    return np.array([[ np.cos(rot),-np.sin(rot),0, xp],
                     [ np.sin(rot), np.cos(rot),0, yp],
                     [ 0,           0,          0, 0 ],
                     [ 0,           0,          0, 1 ]]);    