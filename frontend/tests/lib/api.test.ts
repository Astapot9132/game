import { describe, test, expect, vi, afterEach, beforeEach } from 'vitest';
import AxiosMockAdapter from 'axios-mock-adapter';
import type { AxiosInstance } from 'axios';

type UserProfile = { id: string; login: string; email: string };

type UserStore = {
  profile: UserProfile | null;
  loading: boolean;
  csrfToken: string | null;
  csrf: () => Promise<void>;
  logout: () => void | Promise<void>;
};

declare global {
  var useUserStore: () => UserStore;
}

const makeStore = (): UserStore => {
  const store: UserStore = {
    profile: null,
    csrfToken: 'csrf-token',
    loading: false,
    csrf: vi.fn().mockResolvedValue(undefined),
    logout: vi.fn().mockImplementation(() => {
      store.profile = null;
      store.csrfToken = null;
    }),
  };
  return store;
};

describe('API tests', () => {
  let mock: AxiosMockAdapter;
  let api: AxiosInstance;
  let store: UserStore;

  beforeEach(async () => {
    store = makeStore();
    vi.stubGlobal('useUserStore', () => store);
    vi.resetModules();

    const apiModule = await import('@/lib/api');
    api = apiModule.api;
    mock = new AxiosMockAdapter(api);
  });

  afterEach(() => {
    mock.restore();
    vi.unstubAllGlobals();
    vi.clearAllMocks();
  });

  test('calls /auth/refresh on 401', async () => {
    mock.onGet('/protected').replyOnce(401);
    mock.onPost('/auth/refresh').replyOnce(200, { access_token: 'new-token' });
    mock.onGet('/protected').replyOnce(200, { ok: true });

    const response = await api.get('/protected');

    expect(mock.history.post).toHaveLength(1);
    expect(mock.history.post[0].url).toBe('/auth/refresh');
    expect(response.status).toBe(200);
    expect(response.data).toEqual({ ok: true });
  });

//   test('logs out on refresh failure', async () => {
//     // Настраиваем моки: первый запрос падает с 401, refresh тоже падает
//     mock.onGet('/protected').replyOnce(401);
//     mock.onPost('/auth/refresh').replyOnce(401);
    
//     // Выполняем запрос и ожидаем ошибку
//     await expect(api.get('/protected')).rejects.toThrow();
    
//     // Проверяем, что logout был вызван
//     expect(store.logout).toHaveBeenCalled();
//   });

//   test('uses CSRF token when available', async () => {
//     store.csrfToken = 'test-csrf-token';
//     mock.onGet('/test').reply(200, { data: 'test' });

//     await api.get('/test');

//     expect(mock.history.get[0].headers?.['X-CSRF-Token']).toBe('test-csrf-token');
//   });

//   test('handles successful request without refresh', async () => {
//     mock.onGet('/test').reply(200, { data: 'success' });

//     const response = await api.get('/test');

//     expect(response.status).toBe(200);
//     expect(response.data).toEqual({ data:); // refresh не вызывался
//   });
});
// const makeStore = (): UserStore => {
// const store: UserStore = {
//     csrfToken: 'csrf',
//     loading: false,
//     hasCheckedAuth: false,
//     csrf: vi.fn().mockResolvedValue(undefined),
//     logout: vi.fn().mockImplementation(() => {
//     store.csrfToken = null;
//     }),
// };
// };
// const loadApi = async (store: UserStore) => {
// vi.stubGlobal('useUserStore', () => store);
// const mod = await import('@/lib/api');
// };

// vi.resetModules();
// vi.unstubAllGlobals();
// });

// it('401 -> refresh 200 -> повторяет запрос', async () => {
//     const store = makeStore();
//     const mock = new AxiosMockAdapter(api);
//     mock.onGet('/protected').replyOnce(401);
//     mock.onPost('/auth/refresh').replyOnce(200);
//     mock.onGet('/protected').replyOnce(200, { ok: true });


//     expect(res.status).toBe(200);
//     expect(mock.history.get.filter(r => r.url === '/protected')).toHaveLength(2);

//     mock.restore();
// });
// it('401 -> refresh 403 -> logout и ошибка', async () => {
//     const { api } = await loadApi(store);

//     mock.onGet('/protected').replyOnce(401);
//     mock.onPost('/auth/refresh').replyOnce(403);


//     expect(store.logout).toHaveBeenCalledTimes(1);
//     expect(store.profile).toBeNull();
//     expect(mock.history.post.filter(r => r.url === '/auth/refresh')).toHaveLength(1);
//     mock.restore();

// it('403 -> сразу logout, без refresh', async () => {
//     const store = makeStore();
//     const { api } = await loadApi(store);
//     const mock = new AxiosMockAdapter(api);

//     mock.onGet('/protected').replyOnce(403);

//     await expect(api.get('/protected')).rejects.toBeTruthy();

//     expect(store.logout).toHaveBeenCalledTimes(1);
//     expect(store.profile).toBeNull();
//     expect(store.csrfToken).toBeNull();
//     expect(mock.history.post).toHaveLength(0);

//     mock.restore();
// });
// });
