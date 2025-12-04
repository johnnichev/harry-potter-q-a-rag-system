import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../../../app/App'
import { Source } from '../../../lib/types'

vi.mock('../../../lib/api/client', () => ({
  askStream: async (
    _question: string,
    onStart: (_s: { sources: Source[] }) => void,
    onToken: (_token: string) => void,
    _onEnd: (_payload: {}) => void
  ) => {
    onStart({ sources: [] })
    await Promise.resolve()
    onToken('Hello')
    await Promise.resolve()
    onToken(', world')
  }
}))

test('Shows loading dots before first token and streams assistant message', async () => {
  render(<App />)
  const input = screen.getByRole('textbox', { name: /question/i })
  const button = screen.getByRole('button', { name: /ask chapter/i })
  await userEvent.type(input, 'Test question')
  await userEvent.click(button)
  expect(await screen.findByText('Hello, world')).toBeInTheDocument()
})
