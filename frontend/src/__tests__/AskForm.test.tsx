import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AskForm from '../components/AskForm'

test('Ask button disabled with empty input and during loading', async () => {
  const onAsk = vi.fn(async () => {})
  const { rerender } = render(<AskForm onAsk={onAsk} loading={false} />)
  const button = screen.getByRole('button', { name: /ask chapter/i })
  expect(button).toBeDisabled()

  const input = screen.getByRole('textbox', { name: /question/i })
  await userEvent.type(input, 'Who is Harry Potter?')
  expect(button).not.toBeDisabled()

  // When loading, button is disabled and shows Asking…
  rerender(<AskForm onAsk={onAsk} loading={true} />)
  const loadingButton = screen.getByRole('button', { name: /asking/i })
  expect(loadingButton).toBeDisabled()
})
