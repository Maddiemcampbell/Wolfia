/* eslint-disable */
/* tslint:disable */
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

import { AxiosError, AxiosRequestConfig } from "axios";
import useSWR, { SWRConfiguration } from "swr";
import { api } from "./";
import { Response, UserRequest, UserResponse } from "./data-contracts";

/**
 * Login user and create a user session.
 */
export const login = (data: UserRequest, config?: AxiosRequestConfig) =>
  api.post<any>(`/auth/login`, data, config);

/**
 * Logout user.
 */
export const logout = (data: Response, config?: AxiosRequestConfig) =>
  api.post<any>(`/auth/logout`, data, config);

/**
 * Get the current user.
 */
export const useCurrentUser = (config?: SWRConfiguration<UserResponse>) => {
  return useSWR<UserResponse, AxiosError>(`/auth/me`, config);
};

export const impersonate = (data: { client_user_id: string }) =>
  api.post('/auth/impersonate', data);

export const stopImpersonation = () =>
  api.post('/auth/stop_impersonation');
