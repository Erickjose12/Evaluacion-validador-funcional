const BASE_URL = process.env.BOOKER_URL || 'https://restful-booker.herokuapp.com';

const JSON_HEADERS = { 'Content-Type': 'application/json', Accept: 'application/json' };

const reserva = {
  firstname: 'Ana',
  lastname: 'Lopez',
  totalprice: 150,
  depositpaid: true,
  bookingdates: { checkin: '2026-10-01', checkout: '2026-10-05' },
  additionalneeds: 'Desayuno',
};

async function autenticar(username, password) {
  const res = await fetch(`${BASE_URL}/auth`, {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({ username, password }),
  });
  return { status: res.status, body: await res.json() };
}

let token;

// El token se obtiene UNA sola vez para toda la suite
beforeAll(async () => {
  const { status, body } = await autenticar('admin', 'password123');
  expect(status).toBe(200);
  expect(typeof body.token).toBe('string');
  token = body.token;
});

describe('Ciclo de vida de una reserva', () => {
  let bookingId;

  test('POST /booking crea la reserva y devuelve sus datos', async () => {
    const res = await fetch(`${BASE_URL}/booking`, {
      method: 'POST',
      headers: JSON_HEADERS,
      body: JSON.stringify(reserva),
    });
    const body = await res.json();

    expect(res.status).toBe(200);
    expect(Number.isInteger(body.bookingid)).toBe(true);
    expect(body.booking).toEqual(reserva);
    bookingId = body.bookingid;
  });

  test('GET /booking/:id devuelve la reserva creada', async () => {
    const res = await fetch(`${BASE_URL}/booking/${bookingId}`, { headers: JSON_HEADERS });

    expect(res.status).toBe(200);
    expect(await res.json()).toEqual(reserva);
  });

  test('DELETE /booking/:id con token elimina la reserva', async () => {
    const res = await fetch(`${BASE_URL}/booking/${bookingId}`, {
      method: 'DELETE',
      headers: { Cookie: `token=${token}` },
    });

    // La API responde 201 "Created" al borrar (comportamiento documentado del servicio)
    expect(res.status).toBe(201);
    expect(await res.text()).toBe('Created');
  });

  test('GET /booking/:id de una reserva eliminada responde 404', async () => {
    const res = await fetch(`${BASE_URL}/booking/${bookingId}`);

    expect(res.status).toBe(404);
    expect(await res.text()).toBe('Not Found');
  });
});

describe('Casos negativos', () => {
  test('DELETE sin token responde 403 Forbidden', async () => {
    const crear = await fetch(`${BASE_URL}/booking`, {
      method: 'POST',
      headers: JSON_HEADERS,
      body: JSON.stringify(reserva),
    });
    const { bookingid } = await crear.json();

    const res = await fetch(`${BASE_URL}/booking/${bookingid}`, { method: 'DELETE' });

    expect(res.status).toBe(403);
    expect(await res.text()).toBe('Forbidden');

    // Limpieza: no dejar datos de prueba en el servicio
    await fetch(`${BASE_URL}/booking/${bookingid}`, {
      method: 'DELETE',
      headers: { Cookie: `token=${token}` },
    });
  });

  test('GET de una reserva inexistente responde 404', async () => {
    const res = await fetch(`${BASE_URL}/booking/999999999`);

    expect(res.status).toBe(404);
    expect(await res.text()).toBe('Not Found');
  });

  test('POST /auth con credenciales invalidas no entrega token', async () => {
    const { status, body } = await autenticar('admin', 'clave_incorrecta');

    // Observacion: la API responde 200 en lugar de 401; se valida que no haya token
    expect(status).toBe(200);
    expect(body).toEqual({ reason: 'Bad credentials' });
    expect(body.token).toBeUndefined();
  });
});
