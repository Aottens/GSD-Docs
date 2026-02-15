class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: unknown
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

interface ApiClient {
  get<T>(url: string): Promise<T>
  post<T>(url: string, body?: unknown): Promise<T>
  patch<T>(url: string, body?: unknown): Promise<T>
  delete(url: string): Promise<void>
  postForm<T>(url: string, formData: FormData): Promise<T>
  putForm<T>(url: string, formData: FormData): Promise<T>
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => null)
    throw new ApiError(
      response.status,
      errorData?.detail || response.statusText,
      errorData
    )
  }

  // Handle empty responses (like DELETE)
  const contentType = response.headers.get('content-type')
  if (!contentType?.includes('application/json')) {
    return {} as T
  }

  return response.json()
}

export const api: ApiClient = {
  async get<T>(url: string): Promise<T> {
    const response = await fetch(`/api${url}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return handleResponse<T>(response)
  },

  async post<T>(url: string, body?: unknown): Promise<T> {
    const response = await fetch(`/api${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    })
    return handleResponse<T>(response)
  },

  async patch<T>(url: string, body?: unknown): Promise<T> {
    const response = await fetch(`/api${url}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    })
    return handleResponse<T>(response)
  },

  async delete(url: string): Promise<void> {
    const response = await fetch(`/api${url}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    await handleResponse<void>(response)
  },

  async postForm<T>(url: string, formData: FormData): Promise<T> {
    const response = await fetch(`/api${url}`, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type - browser will set multipart/form-data with boundary
    })
    return handleResponse<T>(response)
  },

  async putForm<T>(url: string, formData: FormData): Promise<T> {
    const response = await fetch(`/api${url}`, {
      method: 'PUT',
      body: formData,
      // Don't set Content-Type - browser will set multipart/form-data with boundary
    })
    return handleResponse<T>(response)
  },
}

export { ApiError }
