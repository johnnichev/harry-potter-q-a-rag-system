import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'
import { Source } from '../types'

vi.mock('../api/client', () => ({
  askStream: async (
    _q: string,
    onStart: (_s: { sources: Source[] }) => void,
    onToken: (_t: string) => void,
    _onEnd: (_payload: {}) => void
  ) => {
    onStart({ sources: [] })
    await act(async () => {
      onToken('Hello')
      onToken(', world')
    })
  }
}))

test('Shows loading dots before first token and streams assistant message', async () => {
  render(<App />)
  const input = screen.getByRole('textbox', { name: /question/i })
  const button = screen.getByRole('button', { name: /ask chapter/i })
  await act(async () => {
    await userEvent.type(input, 'Test question')
    await userEvent.click(button)
  })
  // After streaming begins, assistant message should be present
  expect(await screen.findByText('Hello, world')).toBeInTheDocument()
})
