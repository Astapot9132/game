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

let store: UserStore;


vi.mock('@/stores/user', () => ({
    useUserStore: () => store,
}));

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


  beforeEach(async () => {
    store = makeStore();
//     vi.stubGlobal('useUserStore', () => store);
    vi.resetModules();

    const apiModule = await import('@/lib/api');
    api = apiModule.api;
    mock = new AxiosMockAdapter(api);
  });

  afterEach(() => {
    mock.restore();
//     vi.unstubAllGlobals();
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

//   test('double refresh', async () => {
//     mock.onGet('/protected').replyOnce(401);
//     mock.onPost('/auth/refresh').replyOnce(200, { access_token: 'next-token' });
//     mock.onGet('/protected').replyOnce(401);
//     mock.onPost('/auth/refresh').replyOnce(200, { access_token: 'new-token' });
//     mock.onGet('/protected').replyOnce(200, {ok: true});
//
//
//     const response = await api.get('/protected');
//
//     expect(mock.history.post).toHaveLength(2);
//     expect(mock.history.post[0].url).toBe('/auth/refresh');
//     expect(response.status).toBe(200);
//     expect(response.data).toEqual({ ok: true });
//   });

  test('calls /auth/refresh on 401 then 500', async () => {
    mock.onGet('/protected').replyOnce(401);
    mock.onPost('/auth/refresh').replyOnce(200, { access_token: 'new-token' });
    mock.onGet('/protected').replyOnce(500, { server: 'error' });

    await expect(api.get('/protected')).rejects.toMatchObject({
      response: {
        status: 500,
        data: { server: 'error' },
      },
    });

    expect(mock.history.post).toHaveLength(1);
    expect(mock.history.post[0].url).toBe('/auth/refresh');
  });
})