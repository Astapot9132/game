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
    vi.resetModules();

    const apiModule = await import('@/lib/api');
    api = apiModule.api;
    mock = new AxiosMockAdapter(api);
  });

  afterEach(() => {
    mock.restore();
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
  test.each([
    {
      name: 'double 401 -> error',
      finalData: { server: 'error' },
      finalStatus: 401,
    },
    {
      name: 'calls /auth/refresh on 401 then 500',
      finalData: { server: 'error' },
      finalStatus: 500,
    },
    ])('$name', async ({ finalStatus, finalData }) => {
    mock.onGet('/protected').replyOnce(401);
    mock.onPost('/auth/refresh').replyOnce(200, { access_token: 'new-token' });
    mock.onGet('/protected').replyOnce(finalStatus, finalData);

    await expect(api.get('/protected')).rejects.toMatchObject({
      response: {
        status: finalStatus,
        data: finalData,
      },
    });

    expect(mock.history.get).toHaveLength(2);
    expect(mock.history.post).toHaveLength(1);
    expect(mock.history.post[0].url).toBe('/auth/refresh');
  });
  test('calls /auth/logout on 403', async () => {
    mock.onGet('/protected').replyOnce(403);
    mock.onPost('/auth/logout').replyOnce(200);
    expect(store.csrfToken).not.toBeNull;
    
    await expect(api.get('/protected')).rejects.toMatchObject({
        response: { status: 403 },
      });

    expect(store.logout).toHaveBeenCalledTimes(1);
    expect(store.csrfToken).toBeNull;
  });

})